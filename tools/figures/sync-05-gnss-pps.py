"""sync-05-gnss-pps 그림: PPS 엣지와 NMEA 문장 도착 시각의 관계."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _style import setup, save, COLORS, GRAY

PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
SLUG = "sync-05-gnss-pps"


def _save(fig, name):
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def pps_vs_nmea() -> None:
    rng = np.random.default_rng(11)
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.set_yticks([])
    secs = [0, 1, 2, 3]
    width = 0.1  # 펄스 폭 100 ms
    # PPS 파형
    t = np.linspace(-0.2, 3.8, 4001)
    pps = np.zeros_like(t)
    for k in secs:
        pps[(t >= k) & (t < k + width)] = 1
    ax.plot(t, 2.0 + 0.6 * pps, color=COLORS[0], lw=1.6)
    ax.text(-0.25, 2.3, "PPS", ha="right", va="center", color=COLORS[0])
    # NMEA 문장: 엣지 뒤 수십~수백 ms 사이에 시작, 9600 baud에서 70자 ≈ 73 ms 전송
    tx = 70 * 10 / 9600
    labels = ["12:00:00", "12:00:01", "12:00:02", "12:00:03"]
    for k, lab in zip(secs, labels):
        start = k + 0.12 + rng.uniform(0, 0.25)
        ax.add_patch(plt.Rectangle((start, 0.9), tx, 0.5, color=COLORS[1], alpha=0.8))
        ax.text(start + tx + 0.02, 1.15, f"RMC {lab}", va="center", fontsize=8.5, color=COLORS[1])
        ax.annotate("", xy=(k, 1.55), xytext=(start, 1.55),
                    arrowprops=dict(arrowstyle="->", color=GRAY, lw=0.9))
    ax.text(-0.25, 1.15, "NMEA\n(시리얼)", ha="right", va="center", color=COLORS[1])
    for k in secs:
        ax.axvline(k, color=GRAY, lw=0.8, ls=":", ymin=0.24, ymax=0.95)
    ax.text(0.03, 2.75, "상승 엣지 = 정각", fontsize=9, color=COLORS[0])
    ax.text(1.5, 0.45, "문장 도착은 엣지 뒤 수십~수백 ms에서 흔들린다 → 초 번호만 쓰고, 초 이하는 PPS로 맞춘다",
            ha="center", fontsize=9, color=GRAY)
    ax.set_xlim(-0.2, 3.8)
    ax.set_ylim(0.2, 3.0)
    ax.set_xlabel("시간 [s]")
    ax.set_title("PPS와 NMEA의 역할 분담 (도착 지연은 예시)")
    _save(fig, "pps-vs-nmea")


if __name__ == "__main__":
    setup()
    pps_vs_nmea()
