"""calib-10 레이더-라이다 외부 캘리브레이션 그림.

1. se2-alignment: 리플렉터 대응쌍의 SE(2) 정합 전후(BEV)
2. radar-noise-ellipse: 레이더 측정 오차 타원(거리 방향 일정, 방위 방향 r·σθ로 커짐)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Ellipse, Wedge  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-10-radar-lidar"
setup()


def rot2(a: float) -> np.ndarray:
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


def rigid_2d(src: np.ndarray, dst: np.ndarray) -> tuple[float, np.ndarray]:
    """본문 코드와 같은 닫힌 해(가중치 없음)."""
    mu_s, mu_d = src.mean(axis=0), dst.mean(axis=0)
    S = (src - mu_s).T @ (dst - mu_d)
    yaw = np.arctan2(S[0, 1] - S[1, 0], S[0, 0] + S[1, 1])
    return float(yaw), mu_d - rot2(yaw) @ mu_s


def se2_alignment() -> None:
    rng = np.random.default_rng(2)
    yaw_true, t_true = np.radians(2.5), np.array([3.6, -0.4])
    # 라이다 좌표의 리플렉터 위치(참값)
    lidar = np.c_[rng.uniform(8, 45, 18), rng.uniform(-14, 14, 18)]
    # 레이더 측정: 라이다 → 레이더로 옮긴 뒤 거리·방위 잡음
    R = rot2(yaw_true)
    radar_true = (lidar - t_true) @ R  # R^T (p - t)
    r = np.linalg.norm(radar_true, axis=1) + rng.normal(0, 0.10, len(lidar))
    az = np.arctan2(radar_true[:, 1], radar_true[:, 0]) + np.radians(rng.normal(0, 0.3, len(lidar)))
    radar = np.c_[r * np.cos(az), r * np.sin(az)]
    lidar_meas = lidar + rng.normal(0, 0.03, lidar.shape)
    yaw, t = rigid_2d(radar, lidar_meas)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.4), sharey=True)
    cases = [("정합 전: 레이더 좌표 그대로 겹침", radar), ("정합 후: $R(\\psi)\\,q^R + t$", radar @ rot2(yaw).T + t)]
    for ax, (title, q) in zip(axes, cases):
        ax.scatter(-lidar_meas[:, 1], lidar_meas[:, 0], s=60, facecolors="none", edgecolors=COLORS[0], lw=1.6,
                   label="라이다로 잰 리플렉터 $q^L$", zorder=3)
        ax.scatter(-q[:, 1], q[:, 0], s=22, color=COLORS[1], label="레이더 검출 $q^R$", zorder=4)
        for a, b in zip(lidar_meas, q):
            ax.plot([-a[1], -b[1]], [a[0], b[0]], color=GRAY, lw=0.8, zorder=2)
        res = np.linalg.norm(lidar_meas - q, axis=1)
        ax.text(0.03, 0.97, f"대응점 거리 RMS {np.sqrt(np.mean(res**2)):.2f} m", transform=ax.transAxes, va="top",
                fontsize=10, bbox=dict(fc="white", ec=GRAY))
        ax.set_title(title)
        ax.set_aspect("equal")
        ax.set_xlim(-17, 17)
        ax.set_ylim(-1, 50)
        ax.set_xlabel("좌우 [m] (왼쪽이 좌측)")
        ax.set_xticks([-10, 0, 10])
        ax.set_xticklabels(["10", "0", "10"])
        ax.plot(0, 0, "s", color="k", ms=7)
    axes[0].set_ylabel("전방 [m]")
    axes[1].legend(loc="lower right", fontsize=9.5, frameon=True)
    axes[1].text(0.03, 0.90, f"추정 yaw {np.degrees(yaw):.2f}° (참값 2.50°)\n추정 t = ({t[0]:.2f}, {t[1]:.2f}) m"
                 f"\n(참값 3.60, -0.40)", transform=axes[1].transAxes, va="top", fontsize=9.5, bbox=dict(fc="white", ec="none", alpha=0.9), zorder=10)
    fig.tight_layout()
    save(fig, SLUG, "se2-alignment")


def radar_noise_ellipse() -> None:
    sigma_r, sigma_az = 0.15, np.radians(0.5)
    fig, ax = plt.subplots(figsize=(7.0, 6.0))
    ax.add_patch(Wedge((0, 0), 52, 90 - 35, 90 + 35, color=COLORS[1], alpha=0.06))
    k = 6.0  # 보이게 하려고 타원을 키운다
    for r in (10, 25, 40):
        for a in (-25, 0, 25):
            th = np.radians(a)
            x, y = r * np.cos(th), r * np.sin(th)
            e = Ellipse((-y, x), width=2 * k * r * sigma_az, height=2 * k * sigma_r, angle=-a, fc=COLORS[1],
                        alpha=0.35, ec=COLORS[1])
            ax.add_patch(e)
            ax.plot(-y, x, ".", color="k", ms=3)
        ax.text(-r * np.sin(np.radians(-32)), r * np.cos(np.radians(32)), f"{r} m", fontsize=9, color=GRAY)
    ax.plot(0, 0, "o", color=COLORS[1], ms=9)
    ax.text(0, -2.8, "레이더", ha="center", color=COLORS[1])
    ax.text(-30, 47, f"거리 방향 σ = {sigma_r} m (일정)\n방위 방향 σ = r·{np.degrees(sigma_az):.1f}° (거리에 비례)\n"
            f"(타원은 {k:.0f}σ로 과장)", fontsize=9.5, va="top")
    ax.set_xlim(-32, 32)
    ax.set_ylim(-4, 50)
    ax.set_aspect("equal")
    ax.set_xlabel("좌우 [m]")
    ax.set_ylabel("전방 [m]")
    ax.set_title("레이더 측정 오차는 등방성이 아니다: 원거리일수록 가로로 길다")
    save(fig, SLUG, "radar-noise-ellipse")


if __name__ == "__main__":
    se2_alignment()
    radar_noise_ellipse()
