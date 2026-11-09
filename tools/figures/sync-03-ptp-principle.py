"""sync-03-ptp-principle 그림: E2E 교환 시간-공간 도식(TC 체류 시간), 비대칭이 만드는 오프셋 오차."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _style import setup, save, COLORS, GRAY

PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
SLUG = "sync-03-ptp-principle"


def _save(fig, name):
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def e2e_timeline() -> None:
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    ax.grid(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    ym, yt, ys = 2.0, 1.0, 0.0
    for y, lab in [(ym, "마스터"), (yt, "TC 스위치"), (ys, "슬레이브")]:
        ax.plot([0, 13], [y, y], color="black", lw=1.2)
        ax.text(-0.2, y, lab, ha="right", va="center")
    # Sync: 마스터 t1 → TC 도착 a1, 체류 후 출발 b1 → 슬레이브 t2
    t1, a1, b1, t2 = 0.8, 2.0, 3.4, 4.6
    c_sync = dict(arrowstyle="-|>", color=COLORS[0], lw=1.8)
    ax.annotate("", xy=(a1, yt), xytext=(t1, ym), arrowprops=c_sync)
    ax.plot([a1, b1], [yt, yt], color=COLORS[0], lw=4, alpha=0.35, solid_capstyle="butt")
    ax.annotate("", xy=(t2, ys), xytext=(b1, yt), arrowprops=c_sync)
    ax.text(b1 - 0.05, yt - 0.1, "체류 시간 → correctionField", ha="right", va="top",
            color=COLORS[0], fontsize=9)
    ax.text(1.0, 1.45, "Sync", color=COLORS[0], ha="right", fontsize=10)
    # Follow_Up (t1 전달)
    ax.annotate("", xy=(6.6, ys), xytext=(5.2, ym),
                arrowprops=dict(arrowstyle="-|>", color=COLORS[0], lw=1.2, ls="--"))
    ax.text(6.05, 1.55, "Follow_Up(t₁)", color=COLORS[0], fontsize=9, ha="left")
    # Delay_Req: 슬레이브 t3 → TC → 마스터 t4
    t3, a2, b2, t4 = 7.6, 8.6, 9.6, 10.6
    c_dr = dict(arrowstyle="-|>", color=COLORS[1], lw=1.8)
    ax.annotate("", xy=(a2, yt), xytext=(t3, ys), arrowprops=c_dr)
    ax.plot([a2, b2], [yt, yt], color=COLORS[1], lw=4, alpha=0.35, solid_capstyle="butt")
    ax.annotate("", xy=(t4, ym), xytext=(b2, yt), arrowprops=c_dr)
    ax.text(8.0, 0.45, "Delay_Req", color=COLORS[1], ha="right", fontsize=10)
    ax.annotate("", xy=(12.4, ys), xytext=(11.0, ym),
                arrowprops=dict(arrowstyle="-|>", color=COLORS[1], lw=1.2, ls="--"))
    ax.text(11.75, 1.55, "Delay_Resp(t₄)", color=COLORS[1], fontsize=9, ha="left")
    for x, y, lab, off in [(t1, ym, "t₁", 0.12), (t2, ys, "t₂", -0.12), (t3, ys, "t₃", -0.12), (t4, ym, "t₄", 0.12)]:
        ax.plot(x, y, "o", color="black", ms=5)
        ax.text(x, y + off, lab, ha="center", va="bottom" if off > 0 else "top", fontsize=12)
    ax.text(6.5, -0.55, "o = [(t₂ − t₁ − c_sync) − (t₄ − t₃ − c_req)] / 2", ha="center", va="top", fontsize=11)
    ax.set_xlim(-1.8, 14.2)
    ax.set_ylim(-0.95, 2.45)
    ax.set_title("E2E 지연 요청-응답과 TC의 체류 시간 보정 (two-step)")
    _save(fig, "e2e-timeline")


def asymmetry_error() -> None:
    """경로 비대칭(d_ms - d_sm)과 오프셋 오차의 관계."""
    asym = np.linspace(-2000, 2000, 201)  # ns
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.plot(asym, asym / 2, color=COLORS[0], lw=2)
    ax.axhline(0, color="black", lw=0.8)
    ax.axvline(0, color="black", lw=0.8)
    for x, txt, ty in [(10, "케이블 길이 차 2 m ≈ 10 ns", 800), (400, "PHY·큐 비대칭 400 ns", 450)]:
        ax.plot(x, x / 2, "o", color=COLORS[1])
        ax.annotate(f"{txt} → 오차 {x / 2:g} ns", xy=(x, x / 2), xytext=(-1950, ty),
                    fontsize=9, arrowprops=dict(arrowstyle="-", color=GRAY))
    ax.set_xlabel("경로 비대칭 d_ms − d_sm [ns]")
    ax.set_ylabel("오프셋 오차 [ns]")
    ax.set_title("비대칭은 그 절반이 고정 오프셋 오차가 된다 (도구의 offset 값에는 안 보임)")
    _save(fig, "asymmetry-error")


if __name__ == "__main__":
    setup()
    e2e_timeline()
    asymmetry_error()
