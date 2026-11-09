"""calib-13 시간 오프셋 그림.

1. offset-spatial-error: 시간 오프셋이 만드는 공간 오차(병진: v·Δt, 회전: f·ω·Δt)
2. xcorr-peak: 합성 각속도 크기 신호 두 개와 상호상관 봉우리
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-13-time-offset"
setup()


def offset_spatial_error() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0))
    ax = axes[0]
    v = np.linspace(0, 35, 200)
    for dt, c in ((0.001, COLORS[0]), (0.010, COLORS[1]), (0.050, COLORS[2])):
        ax.plot(v * 3.6, v * dt * 100, color=c, lw=2, label=f"Δt = {dt * 1000:.0f} ms")
    ax.set_xlabel("상대 속도 [km/h]")
    ax.set_ylabel("위치 오차 [cm]")
    ax.set_yscale("log")
    ax.set_ylim(0.1, 300)
    ax.set_yticks([0.1, 1, 10, 100])
    ax.set_yticklabels(["0.1", "1", "10", "100"])
    ax.set_xlim(0, 126)
    ax.set_title("병진: Δx = v·Δt")
    ax.legend(loc="lower right", fontsize=9.5)

    ax = axes[1]
    w = np.linspace(0, 60, 200)
    f = 1000.0
    for dt, c in ((0.005, COLORS[0]), (0.010, COLORS[1]), (0.030, COLORS[2])):
        ax.plot(w, f * np.radians(w) * dt, color=c, lw=2, label=f"Δt = {dt * 1000:.0f} ms")
    ax.axvspan(20, 40, color=GRAY, alpha=0.1)
    ax.text(30, 30, "교차로 회전\n수준 요레이트", ha="center", fontsize=9, color=GRAY)
    ax.set_xlabel("요레이트 [°/s]")
    ax.set_ylabel("가로 픽셀 이동 [px]")
    ax.set_ylim(0, 33)
    ax.set_xlim(0, 60)
    ax.set_title("회전: Δu ≈ f·ω·Δt (f = 1000 px, 거리와 무관)")
    ax.legend(loc="upper left", fontsize=9.5)
    fig.tight_layout()
    save(fig, SLUG, "offset-spatial-error")


def xcorr_peak() -> None:
    rng = np.random.default_rng(5)
    td_true = 0.0225
    dt = 0.001
    t = np.arange(0, 30, dt)

    def wmag(tt: np.ndarray) -> np.ndarray:
        w = np.c_[np.sin(5.3 * tt) + 0.5 * np.sin(11.1 * tt), np.cos(3.7 * tt), 0.8 * np.sin(7.3 * tt + 1)]
        return np.linalg.norm(w, axis=1)

    a = wmag(t) + rng.normal(0, 0.03, len(t))  # IMU
    # 센서 신호: 스탬프 t 의 샘플은 IMU 시각 t + td 의 사건. 30 Hz 차분이라 저역 통과된 모양
    b = wmag(t + td_true)
    k = int(round(1 / 30 / dt))
    b = np.convolve(b, np.ones(k) / k, mode="same") + rng.normal(0, 0.03, len(t))
    an, bn = (a - a.mean()) / a.std(), (b - b.mean()) / b.std()
    max_lag = int(0.2 / dt)
    lags = np.arange(-max_lag, max_lag + 1)
    n = len(an)
    c = np.array([np.dot(an[max(0, L):n + min(0, L)], bn[max(0, -L):n - max(0, L)]) / n for L in lags])
    i = int(np.argmax(c))

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.9), gridspec_kw={"width_ratios": [1.3, 1.0]})
    ax = axes[0]
    m = (t > 10) & (t < 12)
    ax.plot(t[m], a[m], color=COLORS[0], lw=1.2, label="IMU 자이로 $\\|\\omega_{imu}\\|$")
    ax.plot(t[m], b[m], color=COLORS[1], lw=1.6, label="카메라 VO $\\|\\omega_s\\|$ (스탬프 기준)")
    ax.set_xlabel("타임스탬프 [s]")
    ax.set_ylabel("각속도 크기 [rad/s]")
    ax.set_title("두 신호는 모양이 같고 시간축만 밀려 있다")
    ax.legend(loc="upper right", fontsize=9, ncol=1)
    ax.set_ylim(0, 2.6)

    ax = axes[1]
    ax.plot(lags * dt * 1000, c, color=COLORS[2], lw=2)
    ax.axvline(lags[i] * dt * 1000, color=GRAY, ls="--", lw=1)
    ax.plot(lags[i] * dt * 1000, c[i], "o", color=COLORS[1])
    ax.annotate(f"봉우리 τ = {lags[i] * dt * 1000:.0f} ms\n(참값 {td_true * 1000:.1f} ms)", xy=(lags[i] * dt * 1000, c[i]),
                xytext=(60, 0.55), fontsize=10, arrowprops=dict(arrowstyle="->", color="k"))
    ax.set_xlabel("지연 τ [ms]")
    ax.set_ylabel("정규화 상호상관 c(τ)")
    ax.set_title("상호상관이 최대인 지연 = $t_d$")
    ax.set_xlim(-200, 200)
    fig.tight_layout()
    save(fig, SLUG, "xcorr-peak")


if __name__ == "__main__":
    offset_spatial_error()
    xcorr_peak()
