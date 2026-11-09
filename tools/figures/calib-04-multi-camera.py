"""calib-04 스테레오·다중 카메라 그림.

1. stereo-depth-error: 시차 잡음과 상대 yaw 오차가 깊이에 주는 영향
2. surround-layout: 서라운드 뷰 카메라 시야와 겹침 영역, 지면 타깃 배치(위에서 본 그림)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Rectangle, Wedge  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-04-multi-camera"
setup()


def _save(fig: plt.Figure, name: str) -> None:
    prev = os.environ.get("FIGCHECK_DIR")
    if prev:
        fig.savefig(os.path.join(prev, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def stereo_depth_error() -> None:
    f = 1000.0
    Z = np.linspace(2, 60, 400)
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.3))
    ax = axes[0]
    for B, c in ((0.12, COLORS[0]), (0.30, COLORS[2])):
        ax.plot(Z, Z**2 / (f * B) * 0.25, color=c, lw=2, label=f"기선 B = {B:.2f} m")
    ax.set_xlabel("거리 Z [m]")
    ax.set_ylabel("깊이 오차 [m]")
    ax.set_title("시차 오차 0.25 px의 깊이 오차 (f = 1000 px)")
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 8)
    ax.legend(loc="upper left")

    ax = axes[1]
    B = 0.12
    d = f * B / Z
    ax.plot(Z, Z, color=GRAY, lw=1.2, ls="--", label="참값")
    for dpsi, c, lab in ((0.1, COLORS[1], "상대 yaw +0.1°"), (-0.1, COLORS[3], "상대 yaw -0.1°")):
        dd = f * np.radians(dpsi)
        d_est = d + dd
        z_est = np.where(d_est > 0.05, f * B / np.maximum(d_est, 0.05), np.nan)
        ax.plot(Z, z_est, color=c, lw=2, label=f"{lab} (시차 {dd:+.2f} px)")
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 120)
    ax.set_xlabel("참 거리 Z [m]")
    ax.set_ylabel("추정 거리 [m]")
    ax.set_title("상대 yaw 오차가 만드는 깊이 편향 (B = 0.12 m)")
    ax.legend(loc="upper left")
    fig.subplots_adjust(wspace=0.25)
    _save(fig, "stereo-depth-error")


def surround_layout() -> None:
    fig, ax = plt.subplots(figsize=(7.4, 6.4))
    L, Wc = 4.6, 1.9
    ax.add_patch(Rectangle((-L / 2, -Wc / 2), L, Wc, facecolor="#F3F4F6", edgecolor="k", lw=1.5, zorder=3))
    ax.text(0, 0, "차량\n(위에서 본 모습)", ha="center", va="center", fontsize=10, zorder=4)
    cams = [
        ("앞", (L / 2, 0), 0),
        ("뒤", (-L / 2, 0), 180),
        ("왼쪽", (0.3, Wc / 2), 90),
        ("오른쪽", (0.3, -Wc / 2), -90),
    ]
    fov, rad = 190, 3.8
    for (name, p, yaw), c in zip(cams, COLORS):
        ax.add_patch(Wedge(p, rad, yaw - fov / 2, yaw + fov / 2, facecolor=c, alpha=0.12, edgecolor=c, lw=1))
        ax.plot(*p, "o", color=c, ms=8, zorder=5)
        off = np.array([np.cos(np.radians(yaw)), np.sin(np.radians(yaw))]) * 0.45
        ax.text(p[0] + off[0], p[1] + off[1], name, color=c, fontsize=10, ha="center", va="center",
                fontweight="bold", zorder=5)
    # 겹침 영역(모서리)에 지면 타깃
    for sx in (1, -1):
        for sy in (1, -1):
            cx, cy = sx * (L / 2 + 0.9), sy * (Wc / 2 + 0.9)
            ax.add_patch(Rectangle((cx - 0.5, cy - 0.5), 1.0, 1.0, facecolor="white", edgecolor="k", lw=1, zorder=4))
            for i in range(4):
                for j in range(4):
                    if (i + j) % 2 == 0:
                        ax.add_patch(Rectangle((cx - 0.5 + i * 0.25, cy - 0.5 + j * 0.25), 0.25, 0.25,
                                               facecolor="k", lw=0, zorder=4))
    ax.annotate("이웃 카메라가 함께 보는\n모서리에 타깃을 둔다", xy=(L / 2 + 0.9, Wc / 2 + 1.4),
                xytext=(1.0, 4.4), fontsize=10, arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.arrow(-6.0, -4.6, 1.2, 0, head_width=0.15, color="k")
    ax.text(-4.65, -4.6, "x (전방)", va="center", fontsize=9)
    ax.arrow(-6.0, -4.6, 0, 0.9, head_width=0.15, color="k")
    ax.text(-6.0, -3.55, "y (왼쪽)", ha="center", fontsize=9)
    ax.set_xlim(-6.4, 6.4)
    ax.set_ylim(-5, 5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("서라운드 뷰: 어안 카메라 네 대의 시야(약 190°)와 지면 타깃")
    _save(fig, "surround-layout")


if __name__ == "__main__":
    stereo_depth_error()
    surround_layout()
