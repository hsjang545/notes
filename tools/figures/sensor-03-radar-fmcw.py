"""sensor-03-radar-fmcw 그림: 처프와 비트 주파수, Range-Doppler 맵, MIMO 가상 배열."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SLUG = "sensor-03-radar-fmcw"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
C = 299_792_458.0


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def chirp_beat() -> None:
    tc, idle, b = 40.0, 10.0, 1.0       # µs, µs, GHz
    tau = 8.0                           # µs (그림용으로 과장한 왕복 지연)
    period = tc + idle
    t = np.linspace(0, 3 * period, 6000)

    def chirp(tt: np.ndarray) -> np.ndarray:
        ph = tt % period
        return np.where((ph < tc) & (tt >= 0), ph / tc * b, np.nan)

    tx, rx = chirp(t), chirp(t - tau)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.5, 4.8), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    a1.plot(t, tx, color=COLORS[0], lw=2, label="송신 처프")
    a1.plot(t, rx, color=COLORS[1], lw=2, ls="--", label="수신(반사) 처프")
    x0 = 24.0
    y0 = x0 / tc * b
    a1.annotate("", xy=(x0 + tau, y0), xytext=(x0, y0), arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1.2))
    a1.text(6, y0, "τ = 2R/c →", ha="left", va="center", fontsize=9.5)
    a1.annotate("", xy=(x0 + tau, (x0 + tau) / tc * b), xytext=(x0 + tau, y0),
                arrowprops=dict(arrowstyle="<->", color=COLORS[2], lw=1.5))
    a1.annotate("f_b = S·τ", (x0 + tau, y0 + 0.1), (38, 0.3), color=COLORS[2], fontsize=10,
                arrowprops=dict(arrowstyle="->", color=COLORS[2]))
    a1.text(66, 0.12, "기울기 S = B / T_c", fontsize=9.5, color=GRAY)
    a1.set_ylabel("주파수 − f_c [GHz]")
    a1.set_ylim(-0.05, 1.15)
    a1.legend(loc="upper left", fontsize=9)
    beat = tx - rx
    a2.plot(t, beat * 1e3, color=COLORS[2], lw=2)
    a2.set_ylabel("비트 주파수\n[MHz]")
    a2.set_xlabel("시간 [µs]  (τ는 그림용으로 과장)")
    a2.set_ylim(0, 300)
    a2.text(1, 245, "τ 이후 처프 구간에서 일정 → 이 구간을 ADC로 샘플링", fontsize=9, color=GRAY)
    fig.tight_layout()
    out(fig, "chirp-beat")


def range_doppler() -> None:
    """표적 3개와 정지물 여러 개의 IF 신호를 합성해 거리·도플러 2D FFT를 수행한다."""
    rng = np.random.default_rng(0)
    fc, bw, tc, n_s, n_c = 77e9, 300e6, 50e-6, 256, 128
    lam = C / fc
    s = bw / tc
    fs = n_s / tc                      # 복소 샘플링
    t = np.arange(n_s) / fs
    v_ego = 10.0
    targets = [(20.0, -8.0, 1.0), (35.0, 0.0, 0.5), (60.0, 12.0, 0.3)]  # 거리 m, 시선 속도 m/s, 진폭
    # 정지물: 시선 속도 = -v_ego·cos(방위)
    clutter = [(r, -v_ego * np.cos(np.radians(az)), 0.15)
               for r, az in zip(rng.uniform(5, 75, 40), rng.uniform(-70, 70, 40))]
    x = np.zeros((n_c, n_s), complex)
    k = np.arange(n_c)[:, None]
    for r, v, a in targets + clutter:
        rk = r + v * k * tc
        x += a * np.exp(1j * (2 * np.pi * (2 * s * rk / C) * t[None, :] + 4 * np.pi * rk / lam))
    x += (rng.standard_normal(x.shape) + 1j * rng.standard_normal(x.shape)) * 0.1
    win = np.outer(np.hanning(n_c), np.hanning(n_s))
    rd = np.fft.fftshift(np.fft.fft2(x * win), axes=0)
    p = 20 * np.log10(np.abs(rd) + 1e-12)
    p -= p.max()
    r_axis = np.arange(n_s) * C / (2 * bw)                 # 빈 간격 c/(2B)
    v_axis = (np.arange(n_c) - n_c / 2) * lam / (2 * n_c * tc)
    fig, ax = plt.subplots(figsize=(7.8, 4.5))
    im = ax.pcolormesh(r_axis, v_axis, p, cmap="viridis", vmin=-55, vmax=0, shading="auto")
    im.set_rasterized(True)   # SVG 용량을 줄이려고 맵만 래스터로 넣는다
    ax.set_xlim(0, 80)
    ax.set_xlabel("거리 [m]  (거리 FFT)")
    ax.set_ylabel("시선 속도 [m/s]  (도플러 FFT)")
    ax.grid(False)
    for r, v, _ in targets:
        ax.annotate(f"{r:.0f} m, {v:+.0f} m/s", (r, v), (r + 3, v + 4), color="white", fontsize=9,
                    arrowprops=dict(arrowstyle="->", color="white"))
    ax.annotate("정지물: −v·cos(방위)\n(자차 10 m/s)",(70, -9.0), (44, -17.5), color="white", fontsize=9,
                arrowprops=dict(arrowstyle="->", color="white"))
    cb = fig.colorbar(im, ax=ax)
    cb.set_label("상대 세기 [dB]")
    ax.set_title(f"Range-Doppler 맵 (모의: 77 GHz, B = 300 MHz, T_c = 50 µs, 처프 {n_c}개)", loc="left", fontsize=10.5)
    out(fig, "range-doppler")


def mimo_virtual_array() -> None:
    tx = np.array([0.0, 2.0, 4.0])         # λ 단위
    rx = np.array([0.0, 0.5, 1.0, 1.5])
    virt = (tx[:, None] + rx[None, :])
    fig, ax = plt.subplots(figsize=(8.5, 2.9))
    ax.plot(tx, np.full(3, 2), "^", ms=13, color=COLORS[1], label="송신 3개 (간격 2λ)")
    ax.plot(rx, np.full(4, 1), "v", ms=13, color=COLORS[0], label="수신 4개 (간격 λ/2)")
    for i in range(3):
        ax.plot(virt[i], np.zeros(4), "o", ms=11, color=COLORS[2 + i], alpha=0.9)
        ax.text(virt[i].mean(), -0.42, f"Tx{i + 1} × Rx1~4", ha="center", fontsize=9, color=COLORS[2 + i])
    ax.set_yticks([0, 1, 2], ["가상 배열\n12채널", "수신", "송신"])
    ax.set_xticks(np.arange(0, 6, 0.5))
    ax.set_xlabel("안테나 위치 [λ]   (가상 위치 = 송신 위치 + 수신 위치)")
    ax.set_xlim(-0.4, 6.0)
    ax.set_ylim(-0.7, 2.5)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper right", fontsize=9, ncol=1)
    ax.set_title("MIMO 가상 배열: 3 × 4 = 12개 가상 안테나가 λ/2 간격으로 이어짐", loc="left", fontsize=11)
    out(fig, "mimo-virtual-array")


if __name__ == "__main__":
    setup()
    chirp_beat()
    range_doppler()
    mimo_virtual_array()
