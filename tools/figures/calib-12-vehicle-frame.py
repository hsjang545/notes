"""calib-12 차량 좌표계 그림.

1. vehicle-frame: base_link 원점(후륜 차축 중심의 지면 투영), 축, 기하 중심선과 추력선(위·옆에서 본 그림)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-12-vehicle-frame"
setup()

WB, TRACK, L_FRONT, L_REAR, WIDTH = 2.8, 1.6, 0.9, 0.9, 1.85  # 휠베이스, 윤거, 앞·뒤 오버행, 차폭 [m]


def wheel(ax, x: float, y: float, ang_deg: float = 0.0) -> None:
    w, h = 0.65, 0.24
    t = np.radians(ang_deg)
    R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    c = np.array([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2], [-w / 2, -h / 2]]) @ R.T
    # 화면 좌표: 가로 = 차량 x(전방), 세로 = 차량 y(좌측)
    ax.fill(c[:, 0] + x, c[:, 1] + y, color="#374151", zorder=3)


def vehicle_frame() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(9.0, 6.6), gridspec_kw={"height_ratios": [1.35, 1.0]})

    # 위에서 본 그림
    ax = axes[0]
    ax.add_patch(FancyBboxPatch((-L_REAR, -WIDTH / 2), WB + L_FRONT + L_REAR, WIDTH,
                                boxstyle="round,pad=0,rounding_size=0.3", fc="#F3F4F6", ec=GRAY, zorder=1))
    thrust = np.radians(1.5)  # 추력각(과장)
    for x in (0.0,):
        for y in (TRACK / 2, -TRACK / 2):
            wheel(ax, x, y, np.degrees(thrust))
    for y in (TRACK / 2, -TRACK / 2):
        wheel(ax, WB, y, 0.0)
    ax.plot([0, 0], [-TRACK / 2, TRACK / 2], color=GRAY, lw=1, ls=":", zorder=2)
    ax.plot([WB, WB], [-TRACK / 2, TRACK / 2], color=GRAY, lw=1, ls=":", zorder=2)
    # 기하 중심선과 추력선
    ax.plot([-1.6, WB + 2.4], [0, 0], color=COLORS[0], lw=1.6, ls="--", zorder=4)
    ax.text(WB + 2.45, 0.08, "기하 중심선", color=COLORS[0], fontsize=10, va="bottom")
    xe = WB + 2.4
    ax.plot([-1.6, xe], [-1.6 * np.tan(thrust * 4), xe * np.tan(thrust * 4)], color=COLORS[1], lw=1.8, zorder=4)
    ax.text(xe + 0.05, xe * np.tan(thrust * 4) + 0.05, "추력선\n(후륜 진행 방향의 이등분선)", color=COLORS[1],
            fontsize=10, va="bottom")
    ax.annotate("추력각(과장)", xy=(WB + 1.4, 0.5 * (WB + 1.4) * np.tan(thrust * 4)), xytext=(WB + 0.6, -1.25),
                fontsize=10, color=COLORS[1], arrowprops=dict(arrowstyle="->", color=COLORS[1]))
    # base_link 축
    ax.annotate("", xy=(1.0, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#B91C1C", lw=2.2),
                zorder=6)
    ax.annotate("", xy=(0, 1.0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#15803D", lw=2.2),
                zorder=6)
    ax.plot(0, 0, "o", color="k", ms=6, zorder=7)
    ax.text(1.05, -0.22, "x (전방)", color="#B91C1C", fontsize=10)
    ax.text(0.08, 1.05, "y (좌측)", color="#15803D", fontsize=10)
    ax.text(-0.15, -0.35, "base_link\n후륜 차축 중심", fontsize=9.5, ha="right", va="top")
    # 센서(일반 예시)
    sensors = [(1.3, 0.0, "라이다(루프)", COLORS[2]), (1.9, 0.0, "전방 카메라", COLORS[3]),
               (WB + L_FRONT - 0.05, 0.0, "전방 레이더", COLORS[4]), (0.9, -0.3, "IMU", COLORS[5])]
    for x, y, lab, c in sensors:
        ax.plot(x, y, "D", color=c, ms=8, zorder=8, mec="k", mew=0.5)
    ax.text(1.3, 0.28, "라이다", color=COLORS[2], fontsize=9, ha="center", zorder=8)
    ax.text(1.95, -0.32, "카메라", color=COLORS[3], fontsize=9, ha="center", zorder=8)
    ax.text(WB + L_FRONT - 0.05, 0.28, "레이더", color=COLORS[4], fontsize=9, ha="center", zorder=8)
    ax.text(0.9, -0.58, "IMU", color=COLORS[5], fontsize=9, ha="center", zorder=8)
    ax.set_xlim(-2.0, WB + 5.6)
    ax.set_ylim(-1.7, 1.7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("위에서 본 차량 좌표계: 원점, 축, 추력선")

    # 옆에서 본 그림
    ax = axes[1]
    ax.axhline(0, color="k", lw=1.2)
    ax.add_patch(Rectangle((-L_REAR, 0.35), WB + L_FRONT + L_REAR, 0.9, fc="#F3F4F6", ec=GRAY))
    ax.add_patch(Rectangle((0.2, 1.25), 2.2, 0.55, fc="#F3F4F6", ec=GRAY))
    for x in (0.0, WB):
        ax.add_patch(plt.Circle((x, 0.33), 0.33, color="#374151", zorder=3))
        ax.plot(x, 0.33, "o", color="white", ms=3, zorder=4)
    ax.plot([0, 0], [0.33, 0], color=COLORS[0], lw=1, ls=":")
    ax.text(-0.45, 0.25, "후륜 차축 중심을\n다림추로 지면에 투영", fontsize=8.5, color=COLORS[0], ha="right")
    ax.annotate("", xy=(1.0, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#B91C1C", lw=2.2), zorder=6)
    ax.annotate("", xy=(0, 1.0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#1D4ED8", lw=2.2), zorder=6)
    ax.plot(0, 0, "o", color="k", ms=6, zorder=7)
    ax.text(-0.12, 0.95, "z (위)", color="#1D4ED8", fontsize=10, ha="right")
    ax.text(0.95, -0.2, "x", color="#B91C1C", fontsize=10)
    ax.plot(1.3, 1.95, "D", color=COLORS[2], ms=8, mec="k", mew=0.5)
    ax.annotate("", xy=(1.3, 1.95), xytext=(1.3, 0.0), arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1))
    ax.text(1.38, 1.0, "센서 높이 z\n(하중·공기압에 따라 수 cm 변함)", fontsize=9, color=GRAY, bbox=dict(fc="white", ec="none", alpha=0.85))
    ax.plot(WB + L_FRONT - 0.05, 0.55, "D", color=COLORS[4], ms=8, mec="k", mew=0.5)
    ax.set_xlim(-2.0, WB + 5.6)
    ax.set_ylim(-0.4, 2.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("옆에서 본 그림: 원점은 지면 위, z는 지면에 수직")
    fig.tight_layout()
    save(fig, SLUG, "vehicle-frame")


if __name__ == "__main__":
    vehicle_frame()
