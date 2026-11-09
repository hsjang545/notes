"""sync-01-clock-basics 그림: 시계 모델, 정확도와 정밀도."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _style import setup, save, COLORS, GRAY

PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
SLUG = "sync-01-clock-basics"


def _save(fig, name):
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def clock_model() -> None:
    """C(t) - t = θ0 + y0 t + D t²/2 + ε(t). 숫자는 모양을 보이기 위한 가정값."""
    rng = np.random.default_rng(1)
    t = np.linspace(0, 600, 1201)  # s
    theta0 = 0.5e-3
    y0 = 10e-6
    D = 4e-9  # 1/s (모양을 보이려고 과장)
    eps = np.cumsum(rng.normal(0, 20e-6, t.size)) + rng.normal(0, 60e-6, t.size)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(t, np.full_like(t, theta0) * 1e3, color=COLORS[0], lw=1.6, ls="--", label="θ₀ (초기 오프셋)")
    ax.plot(t, (theta0 + y0 * t) * 1e3, color=COLORS[1], lw=1.6, ls="--", label="+ y₀·t (주파수 오차 10 ppm)")
    ax.plot(t, (theta0 + y0 * t + 0.5 * D * t**2) * 1e3, color=COLORS[2], lw=1.6, ls="--",
            label="+ ½D·t² (드리프트, 과장)")
    ax.plot(t, (theta0 + y0 * t + 0.5 * D * t**2 + eps) * 1e3, color=COLORS[6], lw=0.7, alpha=0.8,
            zorder=1, label="+ ε(t) (잡음) = 실제 오프셋")
    ax.set_xlim(0, 600)
    ax.set_xlabel("경과 시간 [s]")
    ax.set_ylabel("오프셋 C(t) − t [ms]")
    ax.set_title("시계 모델: 보정하지 않은 시계의 오프셋 (가정값으로 그린 개념도)")
    ax.legend(loc="upper left")
    _save(fig, "clock-model")


def accuracy_precision() -> None:
    rng = np.random.default_rng(3)
    a = rng.normal(0, 60, 4000)      # 정확하지만 덜 정밀
    b = rng.normal(250, 15, 4000)    # 정밀하지만 치우침(비대칭)
    bins = np.arange(-300, 400, 10)
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.hist(a, bins=bins, color=COLORS[0], alpha=0.6, label="A: 평균 0, 표준편차 60 ns")
    ax.hist(b, bins=bins, color=COLORS[1], alpha=0.6, label="B: 평균 250 ns, 표준편차 15 ns")
    ax.axvline(0, color="black", lw=1.2)
    ax.text(5, ax.get_ylim()[1] * 0.92, "참값(외부 기준)", fontsize=9)
    ax.annotate("", xy=(250, ax.get_ylim()[1] * 0.75), xytext=(0, ax.get_ylim()[1] * 0.75),
                arrowprops=dict(arrowstyle="<->", color=GRAY))
    ax.text(125, ax.get_ylim()[1] * 0.78, "치우침 = 정확도 문제\n(경로 비대칭 등)", ha="center",
            fontsize=9, color=GRAY)
    ax.set_xlabel("외부 기준 대비 오프셋 [ns]")
    ax.set_ylabel("샘플 수")
    ax.set_title("정확도와 정밀도 (모의 데이터)")
    ax.legend(loc="upper left", fontsize=9)
    _save(fig, "accuracy-precision")


if __name__ == "__main__":
    setup()
    clock_model()
    accuracy_precision()
