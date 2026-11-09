"""calib-07 IMU 캘리브레이션 그림 (합성 데이터).

1. bias-growth: 가속도·자이로 바이어스가 적분 후 만드는 위치 오차
2. allan-deviation: 백색 잡음 + 바이어스 불안정성(가우스-마르코프 합으로 근사) + 레이트 랜덤워크의 Allan 편차
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import FuncFormatter, NullFormatter  # noqa: E402
from scipy.signal import lfilter  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-07-imu"
setup()
G = 9.80665
FMT = FuncFormatter(lambda v, _: f"{v:g}")


def _save(fig: plt.Figure, name: str) -> None:
    prev = os.environ.get("FIGCHECK_DIR")
    if prev:
        fig.savefig(os.path.join(prev, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def _logfmt(ax) -> None:
    for a in (ax.xaxis, ax.yaxis):
        a.set_major_formatter(FMT)
        a.set_minor_formatter(NullFormatter())


def bias_growth() -> None:
    t = np.logspace(0, 2.5, 300)
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    for mg, c in ((1, COLORS[0]), (10, COLORS[1])):
        ax.plot(t, 0.5 * mg * 1e-3 * G * t**2, color=c, lw=2, label=f"가속도 바이어스 {mg} mg: ½·b·t²")
    for dph, c in ((10, COLORS[2]), (100, COLORS[3])):
        bg = np.radians(dph) / 3600
        ax.plot(t, G * bg * t**3 / 6, color=c, lw=2, ls="--", label=f"자이로 바이어스 {dph} °/h: g·b·t³/6 (중력 누설)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    _logfmt(ax)
    ax.set_xlim(1, 300)
    ax.set_ylim(1e-3, 1e4)
    ax.set_yticks([0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000])
    ax.set_xlabel("보정 없이 적분한 시간 t [s]")
    ax.set_ylabel("위치 오차 [m]")
    ax.set_title("바이어스가 적분으로 불어나는 속도 (다른 오차가 없을 때)")
    ax.legend(loc="upper left", fontsize=9)
    _save(fig, "bias-growth")


def overlapping_adev(rate: np.ndarray, fs: float, n_taus: int = 60):
    """본문 overlapping_adev와 같은 식."""
    tau0 = 1.0 / fs
    theta = np.concatenate([[0.0], np.cumsum(rate) * tau0])
    m_max = (len(rate) - 1) // 2
    ms = np.unique(np.logspace(0, np.log10(m_max), n_taus).astype(int))
    taus, adev = [], []
    for m in ms:
        d = theta[2 * m:] - 2 * theta[m:-m] + theta[:-2 * m]
        taus.append(m * tau0)
        adev.append(np.sqrt(np.sum(d**2) / (2.0 * (m * tau0) ** 2 * len(d))))
    return np.array(taus), np.array(adev)


def allan_deviation() -> None:
    rng = np.random.default_rng(0)
    fs, hours = 100.0, 4.0
    n = int(fs * 3600 * hours)
    N = 0.15 / 60.0                      # °/s/√Hz  (= 0.15 °/√h)
    K = 0.2 / 3600.0                      # °/s²/√Hz (= 0.2 °/h/√s)
    x = rng.normal(0, N * np.sqrt(fs), n)
    x += np.cumsum(rng.normal(0, K / np.sqrt(fs), n))
    # 바이어스 불안정성: 시정수가 다른 1차 가우스-마르코프 과정의 합으로 근사
    for tc, sig in ((10.0, 1.4), (100.0, 1.4), (1000.0, 1.4)):   # 시정수 [s], 정상 상태 표준편차 [°/h]
        a = np.exp(-1.0 / (fs * tc))
        w = rng.normal(0, sig / 3600.0 * np.sqrt(1 - a * a), n)
        x += lfilter([1.0], [1.0, -a], w)
    tau, ad = overlapping_adev(x, fs)
    ad_h = ad * 3600.0                    # °/h
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.plot(tau, ad_h, color="k", lw=2, label="Allan 편차 (합성 자이로 4시간)")
    tt = np.logspace(-2, 4, 100)
    ax.plot(tt, N * 3600 / np.sqrt(tt), color=COLORS[0], ls="--", lw=1.4, label="기울기 -1/2: N/√τ")
    ax.plot(tt, K * 3600 * np.sqrt(tt / 3), color=COLORS[1], ls="--", lw=1.4, label="기울기 +1/2: K·√(τ/3)")
    j = int(np.argmin(ad_h))
    ax.axhline(ad_h[j], color=COLORS[2], ls="--", lw=1.4, label="기울기 0: 바닥 = 0.664·B")
    ax.plot(1, N * 3600, "o", color=COLORS[0], ms=8)
    ax.annotate(f"τ = 1 s에서 N\n= {N * 3600:.0f} °/h/√Hz = {N * 60:.2f} °/√h", xy=(1, N * 3600),
                xytext=(0.012, 3.0), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.plot(3, K * 3600, "o", color=COLORS[1], ms=8)
    ax.annotate(f"τ = 3 s에서 K = {K * 3600:.1f} °/h/√s", xy=(3, K * 3600), xytext=(8, 0.07), fontsize=9.5,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.plot(tau[j], ad_h[j], "o", color=COLORS[2], ms=8)
    ax.annotate(f"최솟값 {ad_h[j]:.1f} °/h (τ ≈ {tau[j]:.0f} s)\nB ≈ 최솟값 / 0.664 = {ad_h[j] / 0.664:.1f} °/h",
                xy=(tau[j], ad_h[j]), xytext=(60, 9.0), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.axvspan(hours * 3600 / 10, tau[-1] * 1.2, color=GRAY, alpha=0.1, lw=0)
    ax.text(hours * 3600 / 10 * 1.08, 0.04, "레코드\n1/10 이상", fontsize=8.5, color=GRAY, ha="left")
    ax.set_xscale("log")
    ax.set_yscale("log")
    _logfmt(ax)
    ax.set_xlim(0.01, tau[-1] * 1.2)
    ax.set_ylim(0.03, 200)
    ax.set_xlabel("평균 시간 τ [s]")
    ax.set_ylabel("Allan 편차 σ(τ) [°/h]")
    ax.set_title("Allan 편차에서 N, B, K 읽기 (합성 데이터, 참값 N = 0.15 °/√h, K = 0.2 °/h/√s)")
    ax.legend(loc="upper right", fontsize=9)
    _save(fig, "allan-deviation")


if __name__ == "__main__":
    bias_growth()
    allan_deviation()
