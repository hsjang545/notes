"""sync-02-ntp-chrony 그림: NTP 4개 타임스탬프 기하, 오프셋-지연 쐐기 분포."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _style import setup, save, COLORS, GRAY

PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
SLUG = "sync-02-ntp-chrony"


def _save(fig, name):
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def four_timestamps() -> None:
    """시간-공간 도식. 가로축은 참 시간, 두 수평선은 클라이언트·서버."""
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.grid(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    yc, ys = 0.0, 1.0
    ax.plot([0, 10], [yc, yc], color="black", lw=1.2)
    ax.plot([0, 10], [ys, ys], color="black", lw=1.2)
    ax.text(-0.2, yc, "클라이언트", ha="right", va="center")
    ax.text(-0.2, ys, "서버", ha="right", va="center")
    T1, T2, T3, T4 = 1.0, 4.0, 5.2, 7.2   # 참 시간 위치 (d↑=3.0, d↓=2.0: 비대칭)
    arrow = dict(arrowstyle="-|>", color=COLORS[0], lw=1.8)
    ax.annotate("", xy=(T2, ys), xytext=(T1, yc), arrowprops=arrow)
    ax.annotate("", xy=(T4, yc), xytext=(T3, ys), arrowprops=dict(arrow, color=COLORS[1]))
    for x, y, lab, va in [(T1, yc, "t₁", "top"), (T2, ys, "t₂", "bottom"),
                          (T3, ys, "t₃", "bottom"), (T4, yc, "t₄", "top")]:
        ax.plot(x, y, "o", color="black", ms=5)
        ax.text(x, y + (-0.08 if va == "top" else 0.08), lab, ha="center", va=va, fontsize=12)
    ax.text((T1 + T2) / 2 - 0.35, 0.5, "요청\nd↑", color=COLORS[0], ha="right", va="center")
    ax.text((T3 + T4) / 2 + 0.35, 0.5, "응답\nd↓", color=COLORS[1], ha="left", va="center")
    ax.annotate("", xy=(T3, ys + 0.32), xytext=(T2, ys + 0.32),
                arrowprops=dict(arrowstyle="<->", color=GRAY))
    ax.text((T2 + T3) / 2, ys + 0.38, "서버 처리 t₃−t₂", ha="center", va="bottom", color=GRAY, fontsize=9)
    ax.annotate("", xy=(T4, yc - 0.38), xytext=(T1, yc - 0.38),
                arrowprops=dict(arrowstyle="<->", color=GRAY))
    ax.text((T1 + T4) / 2, yc - 0.44, "클라이언트가 잰 왕복 t₄−t₁", ha="center", va="top", color=GRAY, fontsize=9)
    ax.text(8.0, 0.5, "δ = (t₄−t₁) − (t₃−t₂) = d↑ + d↓\n오차 = (d↑ − d↓)/2,  |오차| ≤ δ/2",
            ha="left", va="center", fontsize=10)
    ax.set_xlim(-1.6, 12.6)
    ax.set_ylim(-0.75, 1.65)
    ax.set_title("NTP 한 번의 교환: 4개 타임스탬프와 비대칭 지연")
    _save(fig, "four-timestamps")


def wedge() -> None:
    """지연이 클수록 오프셋 추정이 넓게 퍼지는 쐐기 모양. 모의 데이터."""
    rng = np.random.default_rng(7)
    n = 1500
    base = 100.0  # µs, 최소 왕복 지연
    up = rng.exponential(40, n) * (rng.random(n) < 0.6)   # 요청 방향 큐잉
    dn = rng.exponential(40, n) * (rng.random(n) < 0.6)   # 응답 방향 큐잉
    delay = base + up + dn
    true_offset = 0.0
    est = true_offset + (up - dn) / 2 + rng.normal(0, 2, n)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.scatter(delay, est, s=6, color=COLORS[0], alpha=0.5, label="교환 1회의 (δ, θ) 추정", rasterized=True)
    d = np.linspace(base, delay.max(), 50)
    ax.plot(d, (d - base) / 2, color=COLORS[1], lw=1.5, ls="--", label="±(δ − δ_min)/2 경계")
    ax.plot(d, -(d - base) / 2, color=COLORS[1], lw=1.5, ls="--")
    best = np.argsort(delay)[:30]
    ax.scatter(delay[best], est[best], s=18, color=COLORS[2], label="지연이 가장 작은 샘플")
    ax.axhline(true_offset, color="black", lw=1)
    ax.set_xlabel("왕복 지연 δ [µs]")
    ax.set_ylabel("오프셋 추정 θ − 참값 [µs]")
    ax.set_title("오프셋-지연 산점도: 지연이 작은 샘플일수록 정확하다 (모의 데이터)")
    ax.legend(loc="upper left", fontsize=9)
    _save(fig, "offset-delay-wedge")


if __name__ == "__main__":
    setup()
    four_timestamps()
    wedge()
