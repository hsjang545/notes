"""comm-05-ethernet-sensor-data 그림: 애플리케이션 정지 중 소켓 버퍼 수위와 손실, 필요한 버퍼 크기."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "comm-05-ethernet-sensor-data"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
DEFAULT_RMEM = 212_992


def finish(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def simulate(cap: float, rate_bps: float, pause: tuple[float, float], t_end: float, dt: float = 1e-4):
    """일정한 유입, 애플리케이션은 정지 구간 외에는 즉시 비운다고 가정한 단순 모델."""
    t = np.arange(0, t_end, dt)
    level = np.zeros_like(t)
    dropped = np.zeros_like(t)
    q = 0.0
    lost = 0.0
    inflow = rate_bps / 8 * dt
    for i, ti in enumerate(t):
        q += inflow
        if q > cap:
            lost += q - cap
            q = cap
        if not (pause[0] <= ti < pause[1]):
            q = max(0.0, q - 20 * inflow)   # 애플리케이션이 유입보다 훨씬 빨리 읽음
        level[i] = q
        dropped[i] = lost
    return t, level, dropped


def buffer_fill() -> None:
    rate = 100e6
    pause = (0.020, 0.060)          # 40 ms 정지
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 5.2), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    for cap, label, c in [(DEFAULT_RMEM, "SO_RCVBUF 208 KiB (기본값)", COLORS[1]), (8 * 2**20, "SO_RCVBUF 8 MiB", COLORS[0])]:
        t, level, dropped = simulate(cap, rate, pause, 0.09)
        axes[0].plot(t * 1e3, level / 1e6, color=c, lw=1.8, label=label)
        axes[1].plot(t * 1e3, dropped / 1e6, color=c, lw=1.8)
    for ax in axes:
        ax.axvspan(pause[0] * 1e3, pause[1] * 1e3, color=GRAY, alpha=0.12, lw=0)
    axes[0].text((pause[0] + pause[1]) / 2 * 1e3, 0.58, "애플리케이션 40 ms 정지", ha="center", fontsize=9, color="#374151")
    axes[0].axhline(DEFAULT_RMEM / 1e6, color=COLORS[1], lw=0.8, ls="--")
    axes[0].set_ylabel("버퍼에 쌓인 양 (MB)")
    axes[0].set_ylim(0, 0.65)
    axes[0].legend(loc="upper right", fontsize=9)
    axes[0].set_title("100 Mbit/s UDP 스트림에서 수신이 멈췄을 때 (단순 모델)", fontsize=11)
    axes[1].set_ylabel("누적 손실 (MB)")
    axes[1].set_xlabel("시간 (ms)")
    axes[1].set_ylim(0, 0.45)
    axes[1].text(88, 0.36, "208 KiB는 약 17 ms 뒤 넘치고, 나머지 약 23 ms 분량이 사라진다(RcvbufErrors 증가).",
                 ha="right", fontsize=8.5, color=GRAY)
    fig.text(0.99, -0.01, "모델 가정: 일정한 유입, skb 오버헤드 무시. 실제로는 오버헤드 때문에 더 일찍 넘친다.",
             ha="right", fontsize=8, color=GRAY)
    finish(fig, "buffer-fill")


def required_buffer() -> None:
    pause_ms = np.logspace(0, 3, 200)
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    for i, (rate, label) in enumerate([(10e6, "10 Mbit/s"), (100e6, "100 Mbit/s"), (300e6, "300 Mbit/s"), (1e9, "1 Gbit/s")]):
        need = rate / 8 * pause_ms * 1e-3
        ax.plot(pause_ms, need, color=COLORS[i], lw=1.8, label=label)
    for v, lab in [(DEFAULT_RMEM, "기본 rmem_default·rmem_max 208 KiB"), (64 * 2**20, "예시 설정 64 MiB")]:
        ax.axhline(v, color=GRAY, lw=1, ls="--")
        ax.text(1.1, v * 1.15, lab, fontsize=8.5, color=GRAY)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1, 1000)
    ax.set_ylim(1e3, 1e9)
    ax.set_xlabel("애플리케이션이 멈출 수 있는 최악 시간 (ms)")
    ax.set_ylabel("필요한 수신 버퍼 (바이트)")
    ax.set_yticks([1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9])
    ax.set_yticklabels(["1 kB", "10 kB", "100 kB", "1 MB", "10 MB", "100 MB", "1 GB"])
    ax.set_xticks([1, 10, 100, 1000])
    ax.set_xticklabels(["1", "10", "100", "1000"])
    ax.legend(loc="lower right", fontsize=9, title="데이터율")
    ax.set_title("필요 버퍼 = 데이터율 × 최악 정지 시간 (커널 오버헤드 여유는 별도)", fontsize=11)
    finish(fig, "required-buffer")


if __name__ == "__main__":
    setup()
    buffer_fill()
    required_buffer()
