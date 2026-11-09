"""sensor-00-map 그림: 센서별 대표 거리 범위."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

SLUG = "sensor-00-map"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def range_chart() -> None:
    # (이름, 최소 m, 최대 m, 색, 메모) — 유형별 대표 범위. 제품마다 다르다.
    rows = [
        ("초음파", 0.15, 5, COLORS[6], "주차 보조"),
        ("서라운드 어안 카메라", 0.2, 20, COLORS[0], "근거리 인식"),
        ("코너 레이더(SRR)", 0.2, 80, COLORS[1], "사각지대·교차 경고"),
        ("라이다", 0.3, 200, COLORS[2], "반사율 10%에서 수십~200 m 안팎"),
        ("전방 카메라", 1, 250, COLORS[0], "인식 거리는 해상도·화각에 좌우"),
        ("전방 레이더(LRR)", 0.5, 250, COLORS[1], "기준 RCS에 좌우"),
    ]
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    for i, (name, lo, hi, c, memo) in enumerate(rows):
        ax.barh(i, hi - lo, left=lo, height=0.55, color=c, alpha=0.8)
        ax.text(hi * 1.12, i, memo, va="center", fontsize=9.5, color=GRAY)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.set_xscale("log")
    ax.set_xlim(0.1, 12000)
    ax.set_xticks([0.1, 1, 10, 100, 1000], ["0.1", "1", "10", "100", "1000"])
    ax.set_xlabel("거리 [m] (로그 축)")
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_title("센서 유형별 대표 탐지 거리 범위 (제품·조건에 따라 크게 다름)", loc="left")
    out(fig, "range-chart")


if __name__ == "__main__":
    setup()
    range_chart()
