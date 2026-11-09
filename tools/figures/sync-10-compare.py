"""sync-10-compare 그림: 방식별 전형적인 정밀도 범위(전형값, 측정 아님), 경로 비대칭이 만드는 숨은 편향(합성)."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter

from _style import setup, save, COLORS, GRAY

SLUG = "sync-10-compare"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def _save(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def typical_ranges() -> None:
    """본문 '일반적으로 알려진 수준' 표의 범위를 그대로 옮긴 것. 단위 s."""
    rows = [  # (방식, 하한, 상한, 색)
        ("NTP (LAN, SW 타임스탬프)", 20e-6, 3e-3, COLORS[1]),
        ("NTP (chrony, NIC HW 타임스탬프)", 0.1e-6, 3e-6, COLORS[4]),
        ("PTP (SW 타임스탬프)", 10e-6, 100e-6, COLORS[3]),
        ("PTP (HW, PTP 지원 스위치)", 20e-9, 1e-6, COLORS[0]),
        ("PHC → 시스템 시계 (phc2sys)", 0.2e-6, 5e-6, COLORS[5]),
        ("PPS (커널 PPS, GPIO·시리얼)", 1e-6, 10e-6, COLORS[2]),
        ("PPS (NIC 핀 + ts2phc)", 20e-9, 500e-9, COLORS[6]),
    ]
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    for i, (name, lo, hi, c) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y, np.log10(hi) - np.log10(lo), left=np.log10(lo), height=0.55, color=c, alpha=0.8)
    ax.set_yticks(range(len(rows)), [r[0] for r in reversed(rows)], fontsize=9.5)
    ticks = [-8, -7, -6, -5, -4, -3, -2]
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_major_formatter(FixedFormatter(["10 ns", "100 ns", "1 µs", "10 µs", "100 µs", "1 ms", "10 ms"]))
    ax.set_xlim(-8.2, -2)
    ax.grid(True, axis="x")
    ax.grid(False, axis="y")
    ax.set_axisbelow(True)
    ax.set_xlabel("시간 오차 크기(로그 눈금)")
    ax.set_title("방식별로 흔히 보고되는 오차 범위: 전형값(측정 아님)")
    ax.text(-2.05, -0.9, "장비·망·부하에 따라 한 자릿수 이상 달라진다. 실제 값은 직접 측정한다.",
            ha="right", fontsize=8.5, color=GRAY)
    ax.set_ylim(-1.2, len(rows) - 0.5)
    _save(fig, "typical-ranges")


def asymmetry_bias() -> None:
    """같은 호스트에서 ptp4l 자기 보고 오프셋과 PPS 기준 실제 오차를 함께 기록했다고 가정."""
    rng = np.random.default_rng(5)
    t = np.arange(0, 1200.0)
    load = (t >= 400) & (t < 800)              # 같은 스위치로 대용량 트래픽
    asym = np.where(load, 8e-6, 0.4e-6)          # d_ms − d_sm [s]
    asym = asym + np.where(load, rng.gamma(2, 1.5e-6, t.size), 0)
    true_err = asym / 2 + rng.normal(0, 0.15e-6, t.size)
    self_rep = rng.normal(0, 0.15e-6, t.size) + np.where(load, rng.normal(0, 1.2e-6, t.size), 0)
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    ax.plot(t, self_rep * 1e6, color=COLORS[0], lw=0.8, label="ptp4l 자기 보고 master offset")
    ax.plot(t, true_err * 1e6, color=COLORS[1], lw=0.8, label="PPS 기준으로 잰 실제 오차")
    ax.axvspan(400, 800, color=GRAY, alpha=0.08)
    ax.text(600, 9.5, "네트워크 부하 구간", ha="center", color=GRAY, fontsize=9)
    ax.annotate("편향 ≈ (d_ms − d_sm) / 2\n프로토콜 안에서는 보이지 않음", xy=(700, 5.6), xytext=(850, 7.5),
                arrowprops=dict(arrowstyle="->", color=GRAY), fontsize=9)
    ax.set_xlabel("시간 [s]")
    ax.set_ylabel("오차 [µs]")
    ax.set_ylim(-4, 11)
    ax.set_title("자기 보고 오프셋은 0 근처, 실제 오차는 비대칭의 절반만큼 이동(합성 데이터 예시)")
    leg = ax.legend(loc="upper left", fontsize=9)
    for ln in leg.get_lines():
        ln.set_linewidth(2.5)
    _save(fig, "asymmetry-bias")


if __name__ == "__main__":
    setup()
    typical_ranges()
    asymmetry_bias()
