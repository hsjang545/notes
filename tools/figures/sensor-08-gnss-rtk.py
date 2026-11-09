"""sensor-08-gnss-rtk 그림: 오차원 크기, 보정 방식별 정확도와 수렴 시간, PPS와 NMEA 타이밍."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SLUG = "sensor-08-gnss-rtk"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def error_budget() -> None:
    # (이름, 최소 m, 최대 m, 줄이는 방법) — 본문 표의 대표 범위와 같게 둔다.
    rows = [
        ("수신기 잡음(의사거리)", 0.1, 0.5, "반송파 위상은 mm 수준"),
        ("다중 경로(의사거리)", 0.3, 3, "안테나 위치·접지판·고도각 마스크"),
        ("대류권(모델 적용 전)", 2.3, 10, "천정 약 2.3 m, 저고도각에서 증가 → 모델로 대부분 제거"),
        ("전리층", 2, 15, "이중 주파수로 1차 항 제거"),
        ("위성 궤도·시계", 0.5, 2, "정밀 궤도·시계(PPP), 차분(RTK)"),
    ]
    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    for i, (name, lo, hi, memo) in enumerate(rows):
        ax.barh(i, hi - lo, left=lo, height=0.5, color=COLORS[i], alpha=0.85)
        ax.text(hi * 1.15, i, memo, va="center", fontsize=9, color=GRAY)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.set_xscale("log")
    ax.set_xlim(0.05, 3000)
    ax.set_xticks([0.1, 1, 10, 100], ["0.1", "1", "10", "100"])
    ax.set_xlabel("거리 오차 크기 [m] (로그 축, 단일 주파수 의사거리 기준 대략값)")
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_title("GNSS 의사거리 오차원의 대표 크기 (태양 활동·고도각·환경에 따라 다름)", loc="left", fontsize=11)
    out(fig, "error-budget")


def accuracy_vs_convergence() -> None:
    # (이름, 수렴 시간 범위 s, 수평 정확도 범위 m)
    boxes = [
        ("단독", (1, 30), (1.5, 5)),
        ("SBAS", (1, 60), (0.5, 1.5)),
        ("RTK float", (2, 30), (0.2, 1.0)),
        ("RTK fixed", (5, 60), (0.01, 0.03)),
        ("PPP-RTK", (60, 300), (0.02, 0.1)),
        ("PPP", (900, 3600), (0.03, 0.2)),
    ]
    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    for (lab, (x0, x1), (y0, y1)), c in zip(boxes, COLORS):
        ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, color=c, alpha=0.35, lw=0))
        ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=c, lw=1.5))
        below = lab == "RTK float"
        ax.text(np.sqrt(x0 * x1), y0 / 1.45 if below else y1 * 1.2, lab, ha="center", fontsize=10, color=c)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.5, 1e4)
    ax.set_ylim(0.005, 10)
    ax.set_xticks([1, 10, 60, 600, 3600], ["1 s", "10 s", "1분", "10분", "1시간"])
    ax.set_yticks([0.01, 0.1, 1, 10], ["1 cm", "10 cm", "1 m", "10 m"])
    ax.set_xlabel("초기화·수렴 시간 (대략)")
    ax.set_ylabel("수평 정확도 (대략)")
    ax.set_title("보정 방식별 정확도와 수렴 시간의 대표 범위 (개활지, 제품·서비스마다 다름)", loc="left", fontsize=10.5)
    out(fig, "accuracy-vs-convergence")


def pps_nmea_timing() -> None:
    fig, ax = plt.subplots(figsize=(8.5, 3.2))
    for s in range(4):
        ax.plot([s, s, s + 0.1, s + 0.1], [0, 1, 1, 0], color=COLORS[0], lw=2)
        ax.text(s + 0.02, 1.12, f"PPS\n12:00:0{s}", fontsize=9, color=COLORS[0])
        ax.add_patch(plt.Rectangle((s + 0.25, 1.7), 0.35, 0.4, color=COLORS[1], alpha=0.75))
        ax.text(s + 0.425, 2.25, f"ZDA/RMC\n\"12:00:0{s}\"", ha="center", fontsize=8.5, color=COLORS[1])
        ax.annotate("", (s + 0.05, 1.0), (s + 0.25, 1.75), arrowprops=dict(arrowstyle="->", color=GRAY, lw=1))
    ax.annotate("", (0.25, 1.55), (0.1, 1.55), arrowprops=dict(arrowstyle="<->", color=GRAY))
    ax.annotate("시리얼 지연·흔들림\n(수 ms~수백 ms)", (0.17, 1.52), (0.25, 0.4),
                fontsize=8.5, color=GRAY, arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.plot([0, 4], [0, 0], color="black", lw=0.8)
    ax.set_xlim(-0.1, 4.0)
    ax.set_ylim(-0.1, 2.9)
    ax.set_yticks([])
    ax.set_xticks(range(5), [f"{s} s" for s in range(5)])
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.set_title("PPS는 정확한 순간을, NMEA 문장은 그 순간이 몇 초인지를 알려 준다 (대응 규칙은 수신기 문서로 확인)",
                 loc="left", fontsize=10)
    out(fig, "pps-nmea-timing")


if __name__ == "__main__":
    setup()
    error_budget()
    accuracy_vs_convergence()
    pps_nmea_timing()
