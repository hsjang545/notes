"""sync-09-validate-data 그림: 수신 지연 분포와 간격 지터(합성), 상호상관 지연 추정(합성)."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _style import setup, save, COLORS, GRAY

SLUG = "sync-09-validate-data"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def _save(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def latency_jitter() -> None:
    """30 Hz 카메라 두 가지: 노출 시각 stamp(센서 시계) vs 호스트 수신 시점 stamp."""
    rng = np.random.default_rng(11)
    n = 3000
    t_true = np.arange(n) / 30.0
    transfer = 0.012 + rng.gamma(2.0, 0.0015, n)            # 전송·드라이버 지연 [s]
    recv = t_true + transfer + rng.gamma(1.5, 0.0008, n)     # 녹화기 수신
    stamp_hw = t_true + rng.normal(0, 20e-6, n)               # 센서 시계 stamp
    stamp_rx = t_true + transfer                               # 드라이버가 수신 시점에 찍은 stamp
    cases = [("A. 센서 시계 stamp(노출 시각)", stamp_hw, COLORS[0]),
             ("B. 호스트 수신 시점 stamp", stamp_rx, COLORS[1])]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9))
    bins = np.linspace(0, 30, 121)
    for name, st, c in cases:
        axes[0].hist((recv - st) * 1e3, bins=bins, color=c, alpha=0.6, label=name)
    axes[0].set_xlabel("수신 지연 d = t_recv − t_stamp [ms]")
    axes[0].set_ylabel("메시지 수")
    axes[0].set_title("수신 지연 분포")
    axes[0].legend(loc="upper right", fontsize=8.5)
    width = []
    labels = []
    for name, st, c in cases:
        dt_stamp = np.diff(np.sort(st)) * 1e3 - 1000 / 30
        dt_recv = np.diff(recv) * 1e3 - 1000 / 30
        width += [np.std(dt_stamp), np.std(dt_recv)]
        labels += [f"{name[:2]} stamp 간격", f"{name[:2]} 수신 간격"]
    xs = np.arange(4)
    axes[1].bar(xs, width, color=[COLORS[0], COLORS[0], COLORS[1], COLORS[1]],
                alpha=0.85, hatch=["", "//", "", "//"], edgecolor="white")
    for x, w in zip(xs, width):
        axes[1].text(x, w + 0.08, f"{w:.2f}", ha="center", fontsize=9)
    axes[1].set_xticks(xs, labels, fontsize=9)
    axes[1].set_ylabel("간격 표준편차(지터) [ms]")
    axes[1].set_title("stamp 지터와 수신 지터 비교")
    axes[1].set_ylim(0, max(width) * 1.25)
    fig.suptitle("30 Hz 카메라 두 가지 stamp 방식(합성 데이터 예시)", fontsize=12)
    fig.tight_layout()
    _save(fig, "latency-jitter")


def xcorr_peak() -> None:
    rng = np.random.default_rng(0)
    fs = 1000.0
    t = np.arange(0, 60, 1 / fs)
    k_box = np.ones(150) / 150
    w = np.convolve(np.convolve(rng.standard_normal(t.size), k_box, mode="same"), k_box, mode="same")
    true_lag = 0.0237
    b = -np.interp(t - true_lag, t, w) + 0.15 * w.std() * rng.standard_normal(t.size)
    ga = (w - w.mean()) / w.std()
    gb = (b - b.mean()) / b.std()
    n = t.size
    nfft = 1 << int(np.ceil(np.log2(2 * n)))
    c = np.fft.irfft(np.conj(np.fft.rfft(ga, nfft)) * np.fft.rfft(gb, nfft), nfft) / n
    max_k = 200
    lags = np.arange(-max_k, max_k + 1)
    cc = c[lags % nfft]
    k = int(np.argmax(np.abs(cc)))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.8), gridspec_kw={"width_ratios": [1.3, 1]})
    seg = (t > 20) & (t < 30)
    a1.plot(t[seg], ga[seg], color=COLORS[0], lw=1.5, label="IMU 요레이트(정규화)")
    a1.plot(t[seg], gb[seg], color=COLORS[1], lw=1.2, label="카메라 광류(정규화, 부호 반대)")
    a1.set_xlabel("stamp [s]")
    a1.set_title("두 신호: 모양은 같고 부호·지연이 다름")
    a1.legend(loc="lower left", fontsize=8.5)
    a1.set_ylim(-4, 4)
    a2.plot(lags, cc, color=COLORS[2], lw=1.8)
    a2.axvline(lags[k], color=GRAY, ls="--", lw=1)
    a2.annotate(f"|상관| 최대: {lags[k]:+d} ms\n(넣은 지연 {true_lag * 1e3:.1f} ms)",
                xy=(lags[k], cc[k]), xytext=(-190, -0.8),
                arrowprops=dict(arrowstyle="->", color=GRAY), fontsize=9)
    a2.set_xlabel("지연 τ [ms] (양수 = 카메라 stamp가 늦음)")
    a2.set_ylabel("정규화 상호상관")
    a2.set_title("상호상관과 최대점")
    fig.suptitle("상호상관으로 센서 간 지연 찾기(합성 데이터 예시)", fontsize=12)
    fig.tight_layout()
    _save(fig, "xcorr-peak")


if __name__ == "__main__":
    setup()
    latency_jitter()
    xcorr_peak()
