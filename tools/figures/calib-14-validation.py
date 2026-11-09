"""calib-14 캘리브레이션 검증·유지 관리 그림.

1. loop-consistency: 카메라·라이다·레이더 세 변환의 루프 일관성
2. monitoring-trend: 온라인 지표의 기준선, 임계값, 지속성 판정(합성 예)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-14-validation"
setup()


def loop_consistency() -> None:
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    P = {"카메라": np.array([0.0, 2.6]), "라이다": np.array([-2.4, 0.0]), "레이더": np.array([2.4, 0.0])}
    col = {"카메라": COLORS[0], "라이다": COLORS[2], "레이더": COLORS[1]}
    for k, p in P.items():
        ax.add_patch(plt.Circle(p, 0.55, fc="white", ec=col[k], lw=2.2, zorder=3))
        ax.text(*p, k, ha="center", va="center", fontsize=12, color=col[k], zorder=4)

    def arr(a: str, b: str, label: str, rad: float, off: np.ndarray, color: str) -> None:
        pa, pb = P[a], P[b]
        d = (pb - pa) / np.linalg.norm(pb - pa)
        ax.add_patch(FancyArrowPatch(pa + 0.62 * d, pb - 0.62 * d, connectionstyle=f"arc3,rad={rad}",
                                     arrowstyle="-|>", mutation_scale=18, color=color, lw=2, zorder=2))
        ax.text(*((pa + pb) / 2 + off), label, ha="center", va="center", fontsize=11.5, color=color)

    # 화살표는 점이 옮겨 가는 방향(b 좌표 → a 좌표)으로 그린다
    arr("레이더", "라이다", "$T_{lidar\\_radar}$\n(레이더-라이다)", 0.0, np.array([0.0, -0.45]), "k")
    arr("라이다", "카메라", "$T_{cam\\_lidar}$\n(카메라-라이다)", 0.0, np.array([-1.0, 0.35]), "k")
    arr("레이더", "카메라", "$T_{cam\\_radar}$\n(레이더-카메라)", 0.0, np.array([1.0, 0.35]), "k")
    ax.text(0, 0.45, "$E = T_{cam\\_radar}^{-1}\\,T_{cam\\_lidar}\\,T_{lidar\\_radar}$\n완벽하면 $E = I$",
            ha="center", va="center", fontsize=11, bbox=dict(fc="#F9FAFB", ec=GRAY))
    ax.text(0, -1.25, "불일치 = $\\|\\log R_E\\|$ (각도), $\\|t_E\\|$ (병진)\n어느 변환이 틀렸는지는 알려 주지 않는다",
            ha="center", va="center", fontsize=10, color=GRAY)
    ax.set_xlim(-3.4, 3.4)
    ax.set_ylim(-1.8, 3.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("센서 루프 일관성: 따로 구한 세 변환이 한 바퀴 돌아 제자리로 와야 한다")
    save(fig, SLUG, "loop-consistency")


def monitoring_trend() -> None:
    rng = np.random.default_rng(11)
    days = np.arange(0, 60, 0.25)
    base = 1.0
    x = base + rng.normal(0, 0.08, len(days))
    x[(days > 20) & (days < 20.6)] += 0.6  # 순간 악화(비포장 구간 등)
    x[days > 41] += 0.45  # 브래킷이 틀어진 뒤 지속 악화
    med = np.array([np.median(x[max(0, i - 11):i + 1]) for i in range(len(x))])
    thr = base + 0.3
    fig, ax = plt.subplots(figsize=(9.0, 3.9))
    ax.plot(days, x, ".", color=GRAY, ms=3, label="프레임 묶음별 엣지 정렬 점수(합성)")
    ax.plot(days, med, color=COLORS[0], lw=2, label="이동 중앙값")
    ax.axhline(base, color=COLORS[2], lw=1.2, ls="--", label="캘리브레이션 직후 기준선")
    ax.axhline(thr, color=COLORS[1], lw=1.2, ls=":", label="경고 임계값")
    over = med > thr
    # 3일 이상 연속 초과한 첫 시점
    run = 0
    alarm = None
    for d, o in zip(days, over):
        run = run + 1 if o else 0
        if run >= 12 and alarm is None:
            alarm = d
    ax.annotate("순간 악화: 무시", xy=(20.3, 1.55), xytext=(8, 1.75), fontsize=10,
                arrowprops=dict(arrowstyle="->", color="k"))
    if alarm is not None:
        ax.axvline(alarm, color=COLORS[1], lw=1.5)
        ax.text(alarm - 0.8, 1.85, "지속 초과 → 경고·재캘리브레이션 요청", color=COLORS[1], fontsize=10, ha="right")
    ax.set_xlabel("운행일")
    ax.set_ylabel("점수 (작을수록 좋음)")
    ax.set_ylim(0.6, 2.0)
    ax.set_xlim(0, 60)
    ax.legend(loc="lower right", fontsize=8.8, ncol=2, frameon=True)
    ax.set_title("온라인 모니터링: 기준선 대비 변화와 지속성으로 판단한다")
    save(fig, SLUG, "monitoring-trend")


if __name__ == "__main__":
    loop_consistency()
    monitoring_trend()
