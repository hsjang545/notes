"""calib-00 캘리브레이션 지도 그림.

1. angle-budget: 허용 횡오차와 관심 거리로 정하는 허용 각도 오차
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-00-map"
setup()


def _save(fig: plt.Figure, name: str) -> None:
    """FIGCHECK_DIR 환경변수가 있으면 PNG 미리보기도 남긴다."""
    prev = os.environ.get("FIGCHECK_DIR")
    if prev:
        fig.savefig(os.path.join(prev, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def angle_budget() -> None:
    r = np.linspace(10, 250, 400)
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    for e, c in zip([0.1, 0.2, 0.5, 1.0], COLORS):
        ax.plot(r, np.degrees(e / r), color=c, lw=2, label=f"허용 횡오차 {e:g} m")
    ax.set_yscale("log")
    ax.set_xlabel("관심 최대 거리 r [m]")
    ax.set_ylabel("허용 각도 오차 [°]")
    ax.set_xlim(10, 250)
    ax.set_ylim(0.02, 6)
    ax.set_yticks([0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5])
    ax.set_yticklabels(["0.02", "0.05", "0.1", "0.2", "0.5", "1", "2", "5"])
    ax.plot([100], [np.degrees(0.2 / 100)], "o", color="k", ms=6, zorder=5)
    ax.annotate("100 m에서 0.2 m 허용\n→ 약 0.11°", xy=(100, np.degrees(0.002)),
                xytext=(22, 0.026), fontsize=10,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.set_title("허용 각도 오차 Δθ ≈ e / r")
    ax.legend(loc="upper right")
    _save(fig, "angle-budget")


if __name__ == "__main__":
    angle_budget()
