"""sensor-09-vehicle-signals 그림: CAN 신호의 지연 구조, 저속 휠 속도 양자화."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SLUG = "sensor-09-vehicle-signals"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def can_latency() -> None:
    """실제 요레이트, ECU 필터 출력, 20 ms 주기로 수신된 CAN 값 (모든 수치는 예시)."""
    dt = 0.1e-3
    t = np.arange(-0.05, 0.25, dt)
    true = np.clip((t - 0.0) / 0.05, 0, 1) * 10.0           # 50 ms 동안 0→10 °/s
    tau_f = 0.015                                           # 1차 저역 필터 시상수 15 ms
    filt = np.zeros_like(true)
    for i in range(1, t.size):
        filt[i] = filt[i - 1] + dt / tau_f * (true[i - 1] - filt[i - 1])
    period, phase, d_tx = 0.020, 0.007, 0.002               # 송신 주기, 위상, 송신·전달 지연
    tx_times = np.arange(-0.05 + phase, 0.25, period)
    rx_times = tx_times + d_tx
    rx_vals = np.interp(tx_times, t, filt)
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    ax.plot(t * 1e3, true, color=COLORS[6], lw=2, label="실제 요레이트")
    ax.plot(t * 1e3, filt, color=COLORS[0], lw=2, label="ECU 내부 값(필터 지연 포함)")
    ax.step(rx_times * 1e3, rx_vals, where="post", color=COLORS[1], lw=2, label="로거가 받은 CAN 값(20 ms 주기)")
    ax.plot(rx_times * 1e3, rx_vals, "o", color=COLORS[1], ms=5)
    i = np.argmin(np.abs(filt - 5.0))
    ax.annotate("", (t[i] * 1e3, 5.0), (25, 5.0), arrowprops=dict(arrowstyle="<->", color=GRAY))
    ax.annotate("필터 지연", ((25 + t[i] * 1e3) / 2, 5.0), (55, 2.0), fontsize=9.5,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.annotate("주기 정렬: 새 값이 다음\n송신 때까지 기다림(0~1 주기)", (rx_times[4] * 1e3, rx_vals[4]),
                (110, 4.0), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.set_xlim(-20, 220)
    ax.set_ylim(-0.8, 12.5)
    ax.set_xlabel("시간 [ms]")
    ax.set_ylabel("요레이트 [°/s]")
    ax.legend(loc="lower right", fontsize=9)
    ax.set_title("CAN으로 받은 값은 필터 지연 + 주기 정렬 + 전송 지연만큼 늦다 (예시)", loc="left", fontsize=11)
    out(fig, "can-latency")


def wheel_speed_quantization() -> None:
    """감속 중 휠 속도를 펄스 수(10 ms 창)와 펄스 간격으로 계산했을 때의 차이."""
    n_teeth, r = 48, 0.31
    dist_per_pulse = 2 * np.pi * r / n_teeth          # 약 4 cm
    dt = 1e-4
    t = np.arange(0, 3.0, dt)
    v = np.clip(3.0 - 1.2 * t, 0, None)               # 3 m/s에서 1.2 m/s²로 감속
    s = np.cumsum(v) * dt
    pulse_idx = np.floor(s / dist_per_pulse)
    pulse_t = t[np.flatnonzero(np.diff(pulse_idx) > 0) + 1]
    win = 0.020
    t_w = np.arange(win, 3.0, win)
    counts = np.histogram(pulse_t, bins=np.concatenate([[0], t_w]))[0]
    v_count = counts * dist_per_pulse / win
    v_period = np.full_like(t_w, np.nan)
    for i, tw in enumerate(t_w):
        prev = pulse_t[pulse_t <= tw]
        if prev.size >= 2:
            v_period[i] = dist_per_pulse / (prev[-1] - prev[-2])
            if tw - prev[-1] > 0.1:          # 100 ms 동안 펄스가 없으면 0으로 본다
                v_period[i] = 0.0
    fig, ax = plt.subplots(figsize=(8.0, 4.0))
    ax.step(t_w, v_count * 3.6, where="post", color=COLORS[1], lw=1.0, alpha=0.6, label="펄스 수 방식(20 ms 창)")
    ax.step(t_w, v_period * 3.6, where="post", color=COLORS[0], lw=1.8, label="펄스 간격 방식")
    ax.plot(t, v * 3.6, color=COLORS[6], lw=1.5, ls="--", label="실제 속도")
    ax.set_xlim(0, 3.0)
    ax.set_ylim(-1, 22)
    ax.set_xlabel("시간 [s]")
    ax.set_ylabel("속도 [km/h]")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title(f"저속 휠 속도 양자화 (한 바퀴 {n_teeth}펄스, 반경 {r} m → 펄스당 약 {dist_per_pulse * 100:.0f} cm)",
                 loc="left", fontsize=10.5)
    ax.text(0.05, 20.2, f"펄스 수 방식: 펄스 1개 = 약 {dist_per_pulse / win * 3.6:.1f} km/h 계단", fontsize=9, color=COLORS[1])
    out(fig, "wheel-speed-quantization")


if __name__ == "__main__":
    setup()
    can_latency()
    wheel_speed_quantization()
