"""comm-08-ros2-dds 그림: QoS 호환 행렬, 큰 메시지의 조각 손실 확률."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "comm-08-ros2-dds"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def finish(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def qos_matrix() -> None:
    combos = [("RELIABLE", "TRANSIENT_LOCAL"), ("RELIABLE", "VOLATILE"),
              ("BEST_EFFORT", "TRANSIENT_LOCAL"), ("BEST_EFFORT", "VOLATILE")]
    rank_r = {"BEST_EFFORT": 0, "RELIABLE": 1}
    rank_d = {"VOLATILE": 0, "TRANSIENT_LOCAL": 1}
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    n = len(combos)
    for i, (pr, pd) in enumerate(combos):          # 행: 퍼블리셔(제공)
        for j, (sr, sd) in enumerate(combos):      # 열: 서브스크라이버(요청)
            bad = []
            if rank_r[sr] > rank_r[pr]:
                bad.append("신뢰성")
            if rank_d[sd] > rank_d[pd]:
                bad.append("지속성")
            ok = not bad
            ax.add_patch(Rectangle((j, n - 1 - i), 1, 1, facecolor=COLORS[2] if ok else COLORS[1],
                                   alpha=0.25 if ok else 0.35, edgecolor="white", lw=2))
            txt = "연결" if ok else "연결 안 됨\n(" + "·".join(bad) + ")"
            ax.text(j + 0.5, n - 1 - i + 0.5, txt, ha="center", va="center", fontsize=9)
    labels = [f"{r}\n{d}" for r, d in combos]
    ax.set_xticks(np.arange(n) + 0.5)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_yticks(np.arange(n) + 0.5)
    ax.set_yticklabels(labels[::-1], fontsize=8.5)
    ax.xaxis.tick_top()
    ax.set_xlabel("서브스크라이버가 요청하는 QoS")
    ax.xaxis.set_label_position("top")
    ax.set_ylabel("퍼블리셔가 제공하는 QoS")
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    ax.text(n, -0.15, "요청이 제공보다 엄격하면(BEST_EFFORT ← RELIABLE, VOLATILE ← TRANSIENT_LOCAL) 매칭되지 않는다.",
            ha="right", va="top", fontsize=8.5, color=GRAY)
    finish(fig, "qos-matrix")


def fragment_loss() -> None:
    sizes = np.logspace(3, 7, 300)          # 바이트
    frag_payload = 1480                      # MTU 1500에서 IP 조각 하나가 나르는 데이터
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    for k, p in enumerate([1e-5, 1e-4, 1e-3]):
        n_frag = np.ceil(sizes / frag_payload)
        loss = 1 - (1 - p) ** n_frag
        ax.plot(sizes, loss * 100, color=COLORS[k], lw=1.8, label=f"패킷 손실률 {p * 100:g} %")
    for v, lab in [(100e3, "포인트 클라우드\n(수백 KB)"), (6.2e6, "1080p RGB 이미지\n(약 6 MB)")]:
        ax.axvline(v, color=GRAY, lw=0.9, ls="--")
        ax.text(v / 1.08, 0.0015, lab, fontsize=8.5, color=GRAY, ha="right", va="bottom")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e3, 1e7)
    ax.set_ylim(1e-3, 100)
    ax.set_xticks([1e3, 1e4, 1e5, 1e6, 1e7])
    ax.set_xticklabels(["1 KB", "10 KB", "100 KB", "1 MB", "10 MB"])
    ax.set_yticks([1e-3, 1e-2, 1e-1, 1, 10, 100])
    ax.set_yticklabels(["0.001", "0.01", "0.1", "1", "10", "100"])
    ax.set_xlabel("메시지 크기 (MTU 1500, 조각 하나 약 1.48 KB로 가정)")
    ax.set_ylabel("메시지를 잃을 확률 (%)")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("조각 하나만 잃어도 메시지 전체를 잃는다: 1 − (1 − p)^조각 수 (BEST_EFFORT 가정)", fontsize=10.5)
    finish(fig, "fragment-loss")


if __name__ == "__main__":
    setup()
    qos_matrix()
    fragment_loss()
