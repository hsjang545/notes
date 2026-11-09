"""calib-11 카메라-IMU, 라이다-IMU 캘리브레이션 그림.

1. hand-eye-loop: 두 시각의 IMU·라이다 자세와 A, B, X가 이루는 닫힌 고리(AX = XB)
2. rotation-axes: 운동 쌍의 회전축 분포. 평지 주행(거의 yaw만)과 손으로 흔든 모듈 비교
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-11-imu-extrinsic"
setup()


def frame(ax, origin: np.ndarray, ang: float, color: str, size: float = 0.6) -> None:
    c, s = np.cos(ang), np.sin(ang)
    for v in (np.array([c, s]), np.array([-s, c])):
        ax.annotate("", xy=origin + size * v, xytext=origin, arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6))
    ax.plot(*origin, "o", color=color, ms=5)


def hand_eye_loop() -> None:
    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    poses = [(np.array([0.6, 0.4]), 0.0, "시각 $t_i$"), (np.array([7.2, 0.9]), np.radians(15), "시각 $t_j$")]
    lever = np.array([1.6, 1.6])  # IMU → 라이다 (몸체 좌표)
    imus, lids = [], []
    for c, ang, lab in poses:
        R = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
        box = np.array([[-0.6, -0.6], [2.6, -0.6], [2.6, 2.5], [-0.6, 2.5], [-0.6, -0.6]]) @ R.T + c
        ax.plot(box[:, 0], box[:, 1], color=GRAY, lw=1.0, ls="--")
        imu, lid = c, c + R @ lever
        frame(ax, imu, ang, COLORS[0])
        frame(ax, lid, ang + np.radians(90), COLORS[1])
        ax.text(*(imu + R @ np.array([0.35, -0.35])), "IMU", color=COLORS[0], fontsize=10.5, va="center")
        ax.text(*(lid + R @ np.array([0.25, 0.35])), "라이다", color=COLORS[1], fontsize=10.5, va="center")
        ax.text(*(c + R @ np.array([1.0, 2.8])), lab, ha="center", fontsize=11)
        ax.add_patch(FancyArrowPatch(imu + R @ np.array([-0.15, 0.2]), lid + R @ np.array([-0.25, 0.0]),
                                     connectionstyle="arc3,rad=0.3", arrowstyle="-|>", mutation_scale=15,
                                     color=COLORS[2], lw=2))
        ax.text(*(c + R @ np.array([0.05, 1.25])), "$X$", color=COLORS[2], fontsize=13, ha="center")
        imus.append(imu)
        lids.append(lid)
    ax.add_patch(FancyArrowPatch(imus[0] + [0.2, -0.2], imus[1] + [-0.2, -0.25], connectionstyle="arc3,rad=0.15",
                                 arrowstyle="-|>", mutation_scale=16, color=COLORS[0], lw=2))
    ax.text(4.2, -0.8, "$A = T_{I_i I_j}$ (IMU 상대 운동)", color=COLORS[0], fontsize=11.5, ha="center")
    ax.add_patch(FancyArrowPatch(lids[0] + [0.2, 0.25], lids[1] + [-0.2, 0.25], connectionstyle="arc3,rad=-0.15",
                                 arrowstyle="-|>", mutation_scale=16, color=COLORS[1], lw=2))
    ax.text(4.9, 2.2, "$B = T_{L_i L_j}$\n(라이다 상대 운동)", color=COLORS[1], fontsize=11.5, ha="center")
    ax.add_patch(FancyBboxPatch((11.0, 0.6), 2.4, 1.6, boxstyle="round,pad=0.15", fc="white", ec=GRAY))
    ax.text(12.2, 1.4, "두 경로가 같다\n$A\\,X = X\\,B$\n$X = T_{imu\\_lidar}$", ha="center", va="center",
            fontsize=11)
    ax.set_xlim(-0.5, 13.8)
    ax.set_ylim(-1.2, 4.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("핸드아이 문제: 같은 강체의 두 센서가 같은 운동을 서로 다른 좌표에서 잰다")
    save(fig, SLUG, "hand-eye-loop")


def rotation_axes() -> None:
    rng = np.random.default_rng(3)
    # 평지 주행: 대부분 yaw, roll·pitch는 아주 작다
    drive = np.c_[rng.normal(0, 0.4, 60), rng.normal(0, 0.6, 60), rng.normal(0, 8, 60)]
    # 손으로 흔든 모듈: 세 축 고루
    hand = rng.normal(0, 10, (60, 3))
    fig = plt.figure(figsize=(10.0, 4.8))
    for k, (data, title) in enumerate(((drive, "평지 주행: 회전축이 거의 수직축 하나"),
                                       (hand, "손으로 흔든 모듈: 회전축이 고루 퍼짐"))):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d")
        u = data / np.linalg.norm(data, axis=1, keepdims=True)
        u[u[:, 2] < 0] *= -1  # 축 방향만 보이도록 위쪽 반구로 모은다
        # 단위구 윤곽
        th = np.linspace(0, 2 * np.pi, 80)
        for z in (0.0,):
            ax.plot(np.cos(th), np.sin(th), z, color="#D1D5DB", lw=0.8)
        ax.plot(np.zeros_like(th), np.cos(th), np.sin(th), color="#D1D5DB", lw=0.8)
        ax.plot(np.cos(th), np.zeros_like(th), np.sin(th), color="#D1D5DB", lw=0.8)
        for v in u:
            ax.plot([0, v[0]], [0, v[1]], [0, v[2]], color=COLORS[0], lw=0.6, alpha=0.6)
        ax.scatter(u[:, 0], u[:, 1], u[:, 2], color=COLORS[0], s=10)
        sv = np.linalg.svd(data / np.linalg.norm(data, axis=1).max(), compute_uv=False)
        ax.set_title(title, fontsize=11)
        ax.text2D(0.02, 0.02, "특이값 비 (최소/최대) = %.2f" % (sv[-1] / sv[0]), transform=ax.transAxes, fontsize=10)
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-0.2, 1)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_box_aspect((1, 1, 0.6))
        ax.view_init(elev=18, azim=-60)
        ax.set_xticks([-1, 0, 1])
        ax.set_yticks([-1, 0, 1])
        ax.set_zticks([0, 1])
    fig.suptitle("운동 쌍의 회전축 $\\alpha_i$ 분포와 외부 회전의 관측성", y=0.98)
    save(fig, SLUG, "rotation-axes")


if __name__ == "__main__":
    hand_eye_loop()
    rotation_axes()
