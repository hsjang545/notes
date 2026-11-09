"""calib-09 레이더-카메라 외부 캘리브레이션 그림.

1. elevation-ambiguity: 고도를 재지 않는 레이더는 높이가 다른 점을 같은 (r, θ)로 낸다(옆에서 본 그림)
2. reflector-layout: 리플렉터 배치(위에서 본 그림). 레이더·카메라 시야가 겹치는 영역을 거리·방위로 고루 덮는다
3. error-vs-distance: 오차원별 이미지 오차의 거리 의존성(방위 잡음, 높이 가정 오차, 거리 잡음)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Polygon, Wedge  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-09-radar-camera"
setup()


def elevation_ambiguity() -> None:
    fig, ax = plt.subplots(figsize=(9.0, 4.4))
    radar = np.array([0.0, 0.5])
    cam = np.array([0.6, 1.4])
    ax.axhline(0, color="k", lw=1.2)
    ax.fill_between([-1, 16], -0.9, 0, color="#E5E7EB", zorder=4)
    # 레이더 수직 빔(±8도)
    for a in (-8, 8):
        e = radar + 16 * np.array([np.cos(np.radians(a)), np.sin(np.radians(a))])
        ax.plot([radar[0], e[0]], [radar[1], e[1]], color=COLORS[1], lw=0.8, ls=":")
    ax.add_patch(Wedge(radar, 15.5, -8, 8, color=COLORS[1], alpha=0.07))
    ax.text(13.6, 2.95, "레이더 수직 빔", color=COLORS[1], fontsize=10, ha="center")
    # 같은 경사 거리 r 의 원호와 그 위의 높이가 다른 세 점
    r = 10.0
    ang = np.radians(np.linspace(-8, 8, 50))
    ax.plot(radar[0] + r * np.cos(ang), radar[1] + r * np.sin(ang), color=COLORS[1], lw=2)
    pts = [radar + r * np.array([np.cos(np.radians(a)), np.sin(np.radians(a))]) for a in (-1.2, 2.6, 6.5)]
    labels = ["리플렉터 A (낮음)", "리플렉터 B", "리플렉터 C (높음)"]
    for k, (p, lab) in enumerate(zip(pts, labels)):
        ax.plot(*p, "^", color=COLORS[1], ms=10, zorder=5)
        ax.plot([cam[0], p[0]], [cam[1], p[1]], color=COLORS[0], lw=1.0, alpha=0.8)
        ax.text(p[0] + 0.35, p[1] + 0.08, lab, va="center", fontsize=9.5, zorder=7)
    ax.text(radar[0] + r, -0.5, "레이더 출력은 셋 다 같은 (r, θ)", color=COLORS[1], fontsize=10, ha="center", zorder=7)
    ax.plot(*radar, "o", color=COLORS[1], ms=11, zorder=6)
    ax.text(radar[0] - 0.3, radar[1] + 0.3, "레이더", color=COLORS[1], ha="center")
    ax.plot(*cam, "s", color=COLORS[0], ms=11, zorder=6)
    ax.text(cam[0] - 0.2, cam[1] + 0.35, "카메라", color=COLORS[0], ha="center")
    ax.text(3.2, 2.35, "카메라에서는 세 광선이\n서로 다른 세로 픽셀 v", color=COLORS[0], fontsize=10)
    ax.set_xlim(-1, 16)
    ax.set_ylim(-0.9, 3.6)
    ax.set_xlabel("전방 거리 [m]")
    ax.set_ylabel("높이 [m]")
    ax.set_title("고도를 재지 않는 레이더: 높이 차이가 레이더에서는 사라지고 이미지에서는 세로 오차가 된다")
    ax.set_aspect("equal")
    save(fig, SLUG, "elevation-ambiguity")


def reflector_layout() -> None:
    fig, ax = plt.subplots(figsize=(7.6, 6.2))
    # 위에서 본 그림: 가로축 y(좌측 +)를 화면 왼쪽이 좌측이 되도록 뒤집어 그린다
    ax.add_patch(Polygon([[2.2, 0], [-2.2, 0], [-2.2, 4.6], [2.2, 4.6]], color="#D1D5DB", zorder=1))
    ax.text(0, 2.3, "차량", ha="center", va="center", fontsize=10, zorder=2)
    radar = np.array([0.0, 4.6])
    ax.add_patch(Wedge(radar[[0, 1]], 48, 90 - 45, 90 + 45, color=COLORS[1], alpha=0.08, zorder=0))
    ax.add_patch(Wedge(radar[[0, 1]], 48, 90 - 30, 90 + 30, color=COLORS[0], alpha=0.10, zorder=0))
    ax.text(-24, 32, "레이더 시야", color=COLORS[1], fontsize=10)
    ax.text(-10, 48.5, "카메라 시야(겹치는 영역)", color=COLORS[0], fontsize=10)
    rng_list = [6, 12, 20, 30, 40]
    az_list = [-22, -11, 0, 11, 22]
    k = 0
    for r in rng_list:
        for a in az_list:
            if r == 6 and abs(a) > 15:
                continue
            k += 1
            x = radar[1] + r * np.cos(np.radians(a))
            y = r * np.sin(np.radians(a))
            ax.plot(-y, x, "^", color=COLORS[1], ms=8, zorder=5)
    hold = [(12, 22), (30, -11), (40, 0)]
    for r, a in hold:
        x = radar[1] + r * np.cos(np.radians(a))
        y = r * np.sin(np.radians(a))
        ax.plot(-y, x, "^", mfc="white", mec=COLORS[3], mew=2, ms=11, zorder=6)
    ax.plot([], [], "^", color=COLORS[1], ms=8, label=f"캘리브레이션 위치({k}곳)")
    ax.plot([], [], "^", mfc="white", mec=COLORS[3], mew=2, ms=10, label="검증용으로 빼 둘 위치")
    for r in rng_list:
        th = np.radians(np.linspace(-30, 30, 50))
        ax.plot(-r * np.sin(th), radar[1] + r * np.cos(th), color=GRAY, lw=0.6, ls=":", zorder=0)
        ax.text(-r * np.sin(np.radians(32)), radar[1] + r * np.cos(np.radians(32)), f"{r} m", color=GRAY,
                fontsize=8.5, ha="center")
    ax.set_xlim(-30, 30)
    ax.set_ylim(-1, 53)
    ax.set_aspect("equal")
    ax.set_xlabel("좌우 [m] (왼쪽이 차량 좌측)")
    ax.set_ylabel("전방 [m]")
    ax.set_xticks([-20, -10, 0, 10, 20])
    ax.set_xticklabels(["20", "10", "0", "10", "20"])
    ax.legend(loc="lower right", fontsize=9.5, frameon=True)
    ax.set_title("리플렉터 배치 예: 근·중·원거리 × 좌·중앙·우")
    save(fig, SLUG, "reflector-layout")


def error_vs_distance() -> None:
    f = 1200.0
    Z = np.linspace(3, 60, 300)
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(Z, np.full_like(Z, f * np.radians(0.3)), color=COLORS[0], lw=2, label="방위각 잡음 0.3° → 가로 오차")
    ax.plot(Z, f * 0.3 / Z, color=COLORS[1], lw=2, label="높이 가정 오차 0.3 m → 세로 오차")
    ax.plot(Z, f * 1.0 * 0.15 / Z**2, color=COLORS[2], lw=2, ls="--",
            label="거리 잡음 0.15 m (높이 차 1 m) → 세로 오차")
    ax.set_xlabel("물체까지 깊이 Z [m]")
    ax.set_ylabel("이미지 오차 [px]")
    ax.set_ylim(0, 40)
    ax.set_xlim(0, 60)
    ax.set_title("초점거리 1200 px에서 오차원별 이미지 오차")
    ax.legend(loc="upper right", fontsize=9.5)
    ax.text(30, 3.6, "거리와 무관: 재투영 오차의 바닥", color=COLORS[0], fontsize=9.5)
    save(fig, SLUG, "error-vs-distance")


if __name__ == "__main__":
    elevation_ambiguity()
    reflector_layout()
    error_vs_distance()
