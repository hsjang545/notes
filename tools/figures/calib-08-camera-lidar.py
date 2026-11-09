"""calib-08 카메라-라이다 외부 캘리브레이션 그림.

1. plane-constraint: 보드 평면 하나가 묶는 자유도(법선 방향 거리, 법선 방향)와 묶지 못하는 자유도
2. overlay-before-after: 합성 장면에 라이다 점을 깊이 색으로 투영(틀린 외부 파라미터 vs 맞는 값)
3. rot-vs-trans-error: 회전 오차와 병진 오차가 만드는 픽셀 오차의 거리 의존성
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Polygon  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-08-camera-lidar"
setup()


# ---------------------------------------------------------------- 1. 평면 제약 (옆에서 본 단면)
def plane_constraint() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6), gridspec_kw={"width_ratios": [1.15, 1.0]})

    # 왼쪽: 보드 한 장이 주는 제약 (위에서 본 단면)
    ax = axes[0]
    cam = np.array([0.0, 0.0])
    lid = np.array([0.3, -0.8])
    n = np.array([np.cos(np.radians(-12)), np.sin(np.radians(-12))])  # 센서에서 멀어지는 법선(d > 0)
    along = np.array([-n[1], n[0]])
    d = 3.8
    p0 = d * n + 0.35 * along
    b0, b1 = p0 - 1.2 * along, p0 + 1.2 * along
    ax.plot([b0[0], b1[0]], [b0[1], b1[1]], color="k", lw=4, solid_capstyle="butt", zorder=3)
    ax.text(*(b1 + np.array([0.1, 0.12])), "보드 평면", fontsize=10)
    rng = np.random.default_rng(3)
    s = np.linspace(-1.05, 1.05, 9)
    pts = p0 + np.outer(s, along) + np.outer(rng.normal(0, 0.035, len(s)), n)
    for q in pts:
        ax.plot([lid[0], q[0]], [lid[1], q[1]], color=COLORS[1], lw=0.6, alpha=0.35)
    ax.scatter(pts[:, 0], pts[:, 1], s=20, color=COLORS[1], zorder=5)
    ax.text(*(b0 + np.array([0.15, -0.3])), "라이다 점 $p_i^L$\n(카메라 좌표로 옮긴 뒤)", color=COLORS[1], fontsize=9.5)
    foot = d * n
    ax.annotate("", xy=foot, xytext=cam, arrowprops=dict(arrowstyle="->", color=COLORS[0], lw=1.6))
    ax.text(*(0.5 * foot + np.array([0.0, 0.18])), "$d_c$", color=COLORS[0], fontsize=13)
    ax.annotate("", xy=foot + 0.9 * n, xytext=foot, arrowprops=dict(arrowstyle="-|>", color=COLORS[0], lw=1.8))
    ax.text(*(foot + 0.95 * n + np.array([0.05, -0.05])), "$n_c$", color=COLORS[0], fontsize=13)
    ax.plot(*cam, "s", color=COLORS[0], ms=10)
    ax.text(cam[0], cam[1] + 0.3, "카메라", color=COLORS[0], ha="center")
    ax.plot(*lid, "o", color=COLORS[1], ms=10)
    ax.text(lid[0], lid[1] - 0.42, "라이다", color=COLORS[1], ha="center")
    ax.text(-0.4, 1.95, r"잔차 $r_i = n_c^\top (R\, p_i^L + t) - d_c$", fontsize=11)
    ax.set_title("보드 한 자세: 라이다 점이 카메라가 본 평면 위에 있어야 한다", fontsize=11)
    ax.set_xlim(-0.6, 5.6)
    ax.set_ylim(-2.0, 2.3)
    ax.set_aspect("equal")
    ax.axis("off")

    # 오른쪽: 묶이는 자유도와 안 묶이는 자유도
    ax = axes[1]
    x0 = 2.0
    ax.plot([x0, x0], [-1.2, 1.2], color="k", lw=4)
    ax.text(x0 + 0.08, 1.3, "보드 평면", fontsize=10)
    ax.add_patch(FancyArrowPatch((x0 + 0.15, 0.0), (x0 + 1.0, 0.0), arrowstyle="<|-|>",
                                 mutation_scale=14, color=COLORS[2], lw=2))
    ax.text(x0 + 0.25, -0.45, "법선 방향 이동\n잔차가 바로 커짐\n(묶임)", va="top", color=COLORS[2], fontsize=10)
    ax.add_patch(FancyArrowPatch((x0 - 0.3, -1.0), (x0 - 0.3, 1.0), arrowstyle="<|-|>",
                                 mutation_scale=14, color=COLORS[3], lw=2))
    ax.text(x0 - 0.45, 0.0, "면 안에서\n미끄러짐\n잔차 그대로\n(안 묶임)", ha="right", va="center", color=COLORS[3],
            fontsize=10)
    th = np.linspace(np.radians(-150), np.radians(150), 60)
    cx, cy = x0 + 0.0, 1.75
    ax.plot(cx + 0.45 * np.cos(th), cy + 0.15 * np.sin(th), color=COLORS[3], lw=1.6)
    ax.annotate("", xy=(cx + 0.45 * np.cos(th[-1]), cy + 0.15 * np.sin(th[-1])),
                xytext=(cx + 0.45 * np.cos(th[-4]), cy + 0.15 * np.sin(th[-4])),
                arrowprops=dict(arrowstyle="-|>", color=COLORS[3]))
    ax.text(cx + 0.6, cy, "법선 축 회전(안 묶임)", color=COLORS[3], fontsize=10, va="center")
    ax.text(0.0, -1.55, "평면 하나 = 3자유도(법선 방향 2 + 거리 1)\n법선이 서로 다른 자세 3개 이상 → 6자유도", fontsize=10,
            va="top")
    ax.set_title("평면 하나가 정하는 것과 못 정하는 것", fontsize=11)
    ax.set_xlim(-0.2, 4.4)
    ax.set_ylim(-2.4, 2.3)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    save(fig, SLUG, "plane-constraint")


# ---------------------------------------------------------------- 2. 투영 오버레이 (합성 장면)
K = np.array([[900.0, 0, 640], [0, 900.0, 360], [0, 0, 1]])
W, H = 1280, 720
CAM_H = 1.5  # 카메라 높이 [m]
R_OPT = np.array([[0, -1, 0], [0, 0, -1], [1, 0, 0]], float)  # 몸체(x 전방) -> 광학(z 전방)


def rot_zyx(yaw: float, pitch: float, roll: float) -> np.ndarray:
    cy, sy, cp, sp, cr, sr = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch), np.cos(roll), np.sin(roll)
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    return Rz @ Ry @ Rx


def project(P_body: np.ndarray, R_err: np.ndarray, t_err: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """카메라 몸체 좌표(카메라 위치 원점) 점을 투영. 외부 파라미터 오차 R_err, t_err를 넣는다."""
    Pc = (P_body @ R_err.T + t_err) @ R_OPT.T
    m = Pc[:, 2] > 0.5
    uv = Pc[m] @ K.T
    uv = uv[:, :2] / uv[:, 2:3]
    return uv, Pc[m, 2]


# 장면: 지면, 상자 두 개(차량 대용), 기둥 세 개. 모두 카메라 몸체 좌표(x 전방, y 좌측, z 위, 원점 = 카메라)
BOXES = [  # (x 앞면, y 중심, 폭, 높이, 깊이)
    (9.0, 1.8, 1.8, 1.5, 4.0),
    (17.0, -2.5, 1.8, 1.6, 4.0),
]
POLES = [(6.0, -3.2, 3.2), (14.0, 4.2, 3.5), (26.0, -5.5, 4.0)]  # (x, y, 높이)


def scene_polygons() -> list[tuple[np.ndarray, str]]:
    """이미지에 그릴 다각형(맞는 외부 파라미터로 투영)."""
    polys = []
    I = np.eye(3)
    z0 = np.zeros(3)
    for x, y, w, h, dpt in BOXES:
        front = np.array([[x, y - w / 2, -CAM_H], [x, y + w / 2, -CAM_H], [x, y + w / 2, -CAM_H + h],
                          [x, y - w / 2, -CAM_H + h]])
        side_y = y + w / 2 if y < 0 else y - w / 2
        side = np.array([[x, side_y, -CAM_H], [x + dpt, side_y, -CAM_H], [x + dpt, side_y, -CAM_H + h],
                         [x, side_y, -CAM_H + h]])
        for P, c in ((side, "#9CA3AF"), (front, "#6B7280")):
            uv, _ = project(P, I, z0)
            polys.append((uv, c))
    for x, y, h in POLES:
        P = np.array([[x, y - 0.12, -CAM_H], [x, y + 0.12, -CAM_H], [x, y + 0.12, -CAM_H + h],
                      [x, y - 0.12, -CAM_H + h]])
        uv, _ = project(P, I, z0)
        polys.append((uv, "#4B5563"))
    return polys


def lidar_points() -> np.ndarray:
    """회전형 라이다 흉내: 수직 채널 32개, 수평 0.2도. 각 광선이 지면·상자·기둥과 만나는 첫 점."""
    origin = np.array([-0.3, 0.0, 0.25])  # 라이다는 카메라 약간 뒤·위 (점은 카메라 몸체 좌표로 표현)
    elev = np.radians(np.linspace(-16, 4, 32))
    azim = np.radians(np.arange(-45, 45, 0.2))
    E, A = np.meshgrid(elev, azim)
    d = np.c_[(np.cos(E) * np.cos(A)).ravel(), (np.cos(E) * np.sin(A)).ravel(), np.sin(E).ravel()]
    best = np.full(len(d), np.inf)
    # 지면 z = -CAM_H
    with np.errstate(divide="ignore", invalid="ignore"):
        tg = (-CAM_H - origin[2]) / d[:, 2]
    best = np.where((tg > 0) & (tg < 40), tg, best)
    for x, y, w, h, dpt in BOXES:
        # 앞면 x = x
        with np.errstate(divide="ignore", invalid="ignore"):
            tf = (x - origin[0]) / d[:, 0]
        p = origin + tf[:, None] * d
        ok = (tf > 0) & (np.abs(p[:, 1] - y) < w / 2) & (p[:, 2] > -CAM_H) & (p[:, 2] < -CAM_H + h)
        best = np.where(ok & (tf < best), tf, best)
        side_y = y + w / 2 if y < 0 else y - w / 2
        with np.errstate(divide="ignore", invalid="ignore"):
            ts = (side_y - origin[1]) / d[:, 1]
        p = origin + ts[:, None] * d
        ok = (ts > 0) & (p[:, 0] > x) & (p[:, 0] < x + dpt) & (p[:, 2] > -CAM_H) & (p[:, 2] < -CAM_H + h)
        best = np.where(ok & (ts < best), ts, best)
    for x, y, h in POLES:
        with np.errstate(divide="ignore", invalid="ignore"):
            tp = (x - origin[0]) / d[:, 0]
        p = origin + tp[:, None] * d
        ok = (tp > 0) & (np.abs(p[:, 1] - y) < 0.12) & (p[:, 2] > -CAM_H) & (p[:, 2] < -CAM_H + h)
        best = np.where(ok & (tp < best), tp, best)
    m = np.isfinite(best)
    return origin + best[m, None] * d[m]


def overlay_before_after() -> None:
    polys = scene_polygons()
    P = lidar_points()
    cases = [
        ("외부 파라미터 오차: yaw 1.5°, pitch 0.8°, 병진 10 cm", rot_zyx(np.radians(1.5), np.radians(0.8), 0.0),
         np.array([0.0, 0.10, 0.0])),
        ("캘리브레이션 후", np.eye(3), np.zeros(3)),
    ]
    fig, axes = plt.subplots(2, 1, figsize=(8.0, 9.4))
    for ax, (title, Re, te) in zip(axes, cases):
        ax.add_patch(Polygon([[0, 0], [W, 0], [W, H * 0.5], [0, H * 0.5]], color="#E5E7EB", zorder=0))  # 하늘
        ax.add_patch(Polygon([[0, H * 0.5], [W, H * 0.5], [W, H], [0, H]], color="#D1D5DB", zorder=0))  # 지면
        for uv, c in polys:
            ax.add_patch(Polygon(uv, closed=True, color=c, zorder=1))
        uv, depth = project(P, Re, te)
        m = (uv[:, 0] >= 0) & (uv[:, 0] < W) & (uv[:, 1] >= 0) & (uv[:, 1] < H)
        order = np.argsort(-depth[m])
        sc = ax.scatter(uv[m][order, 0], uv[m][order, 1], c=depth[m][order], cmap="turbo_r", vmin=2, vmax=30,
                        s=1.2, linewidths=0, zorder=2, rasterized=True)
        ax.set_xlim(0, W)
        ax.set_ylim(H, 0)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for sp in ax.spines.values():
            sp.set_visible(True)
            sp.set_color(GRAY)
        ax.set_title(title)
    cb = fig.colorbar(sc, ax=axes, shrink=0.5, pad=0.02)
    cb.set_label("카메라 깊이 Z [m]")
    axes[0].annotate("기둥·상자 모서리에서\n색 경계가 어긋남", xy=(395, 330), xytext=(60, 120), fontsize=10,
                     arrowprops=dict(arrowstyle="->", color="k"), bbox=dict(fc="white", ec=GRAY, alpha=0.9))
    fig.set_dpi(160)  # 점은 래스터로 넣어 SVG 크기를 줄인다
    save(fig, SLUG, "overlay-before-after")


# ---------------------------------------------------------------- 3. 회전 vs 병진 오차
def rot_vs_trans_error() -> None:
    f = 1000.0
    Z = np.linspace(2, 60, 300)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for dth, c in ((0.1, COLORS[0]), (0.3, COLORS[5])):
        ax.plot(Z, np.full_like(Z, f * np.radians(dth)), color=c, lw=2, label=f"회전 오차 {dth}°")
    for dt, c in ((0.02, COLORS[1]), (0.05, COLORS[4])):
        ax.plot(Z, f * dt / Z, color=c, lw=2, ls="--", label=f"병진 오차 {dt * 100:.0f} cm")
    ax.set_xlabel("물체까지 깊이 Z [m]")
    ax.set_ylabel("이미지 어긋남 [px]")
    ax.set_title("초점거리 1000 px에서 외부 파라미터 오차가 만드는 픽셀 오차")
    ax.set_ylim(0, 12)
    ax.set_xlim(0, 60)
    ax.text(40, 6.0, "회전: 거리와 무관 ($f\\,\\delta\\theta$)", color=COLORS[5], fontsize=10)
    ax.text(12, 9.5, "병진: 거리에 반비례 ($f\\,\\delta t / Z$)", color=COLORS[4], fontsize=10)
    ax.legend(loc="upper right", ncol=2, fontsize=9.5)
    save(fig, SLUG, "rot-vs-trans-error")


if __name__ == "__main__":
    plane_constraint()
    overlay_before_after()
    rot_vs_trans_error()
