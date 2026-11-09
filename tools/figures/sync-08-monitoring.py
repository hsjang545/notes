"""sync-08-monitoring 그림: 합성 데이터로 만든 모니터링 그래프 예시(시계열, 분포와 경고 임계값)."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from _style import setup, save, COLORS, GRAY

SLUG = "sync-08-monitoring"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def _save(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def synth_ptp4l(seed: int = 3) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """1 Hz ptp4l 로그를 흉내 낸 합성 시계열: 수렴, 경로 변경(계단), 링크 끊김 뒤 재수렴."""
    rng = np.random.default_rng(seed)
    t = np.arange(0, 1800.0)
    off = rng.normal(0, 25, t.size)
    off[:40] += 4000 * np.exp(-t[:40] / 8) * np.cos(t[:40] / 3)  # 시작 수렴
    delay = 1230 + rng.normal(0, 3, t.size)
    delay[t >= 700] += 180  # 경로 변경: path delay 계단
    off[(t >= 700) & (t < 760)] += 600 * np.exp(-(t[(t >= 700) & (t < 760)] - 700) / 12)
    gap = (t >= 1200) & (t < 1230)  # 링크 끊김: 기록 없음
    rec = (t >= 1230) & (t < 1300)
    off[rec] += 2500 * np.exp(-(t[rec] - 1230) / 10)
    off[gap] = np.nan
    delay[gap] = np.nan
    return t, off, delay


def timeseries() -> None:
    t, off, delay = synth_ptp4l()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.4, 5.2), sharex=True,
                                 gridspec_kw={"height_ratios": [1.6, 1]})
    a1.plot(t, off, "-", lw=0.7, color=COLORS[0])
    a1.set_yscale("symlog", linthresh=100)
    a1.set_ylim(-6000, 20000)
    a1.set_yticks([-1000, -100, 0, 100, 1000, 10000])
    a1.set_yticklabels(["-1000", "-100", "0", "100", "1000", "10000"])
    a1.axhspan(-1000, 1000, color=COLORS[2], alpha=0.06)
    a1.axhline(1000, color=COLORS[1], ls="--", lw=1)
    a1.text(1795, 1500, "경고 임계값 1 µs", color=COLORS[1], fontsize=9, ha="right")
    a1.set_ylabel("master offset [ns]\n(±100 ns 밖은 로그)")
    notes = [(20, "시작 수렴(통계 제외)"), (700, "경로 변경"), (1200, "링크 끊김 → 공백")]
    for x, txt in notes:
        a1.axvline(x, color=GRAY, ls=":", lw=1)
        a1.text(x + 12, 9000, txt, color=GRAY, fontsize=9, va="center", bbox=dict(facecolor="white", edgecolor="none", pad=1))
    a2.plot(t, delay, "-", lw=0.7, color=COLORS[3])
    a2.set_ylabel("path delay [ns]")
    a2.set_xlabel("시간 [s]")
    for x, _ in notes[1:]:
        a2.axvline(x, color=GRAY, ls=":", lw=1)
    a1.set_title("ptp4l 오프셋과 경로 지연 시계열(합성 데이터 예시)")
    fig.tight_layout()
    _save(fig, "offset-timeseries")


def histogram() -> None:
    t, off, _ = synth_ptp4l()
    x = off[(t >= 60) & ~np.isnan(off)]
    a = np.abs(x)
    p99 = np.percentile(a, 99)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.8))
    a1.hist(x[np.abs(x) < 300], bins=60, color=COLORS[0], alpha=0.85)
    a1.set_xlabel("master offset [ns] (|값| < 300만)")
    a1.set_ylabel("표본 수")
    a1.set_title("분포: 대부분은 0 근처")
    srt = np.sort(a)
    ccdf = 1.0 - np.arange(srt.size) / srt.size
    a2.loglog(srt, ccdf, color=COLORS[0], lw=2)
    a2.axvline(p99, color=COLORS[2], ls="--", lw=1.2)
    a2.text(p99 * 0.85, 0.0015, f"p99_abs ≈ {p99:.0f} ns", color=COLORS[2], fontsize=9, ha="right")
    a2.axvline(1000, color=COLORS[1], ls="--", lw=1.2)
    a2.text(1100, 0.12, "임계값\n1 µs", color=COLORS[1], fontsize=9)
    a2.axvline(a.max(), color=GRAY, ls=":", lw=1)
    a2.text(a.max() * 1.1, 0.002, "max_abs", color=GRAY, fontsize=9, ha="left")
    a2.set_xlim(1, 2e4)
    a2.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    a2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    a2.set_xlabel("|offset| [ns] (로그)")
    a2.set_ylabel("|offset|이 이 값보다 클 비율")
    a2.set_title("꼬리: p99와 최댓값은 따로 본다")
    fig.suptitle("수렴 구간(앞 60초)을 뺀 오프셋 통계(합성 데이터 예시)", fontsize=12)
    fig.tight_layout()
    _save(fig, "offset-stats")


if __name__ == "__main__":
    setup()
    timeseries()
    histogram()
