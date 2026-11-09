"""sync-04-linuxptp-ubuntu 그림: ptp4l 서보 상태(s0→s1→s2)와 수렴 개념도."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from _style import setup, save, COLORS, GRAY

PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
SLUG = "sync-04-linuxptp-ubuntu"


def _save(fig, name):
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def simulate():
    """1 s 주기 PI 서보 모의. 주파수 오차 +13.5 ppm, 초기 오프셋 -8.3 ms(가정값)."""
    rng = np.random.default_rng(5)
    n = 40
    true_freq_err = 13500.0  # ppb, 로컬 시계가 빠름
    offset = -8.31e6         # ns
    kp, ki = 0.7, 0.3        # linuxptp 기본 PI 계수와 같은 값
    freq = 0.0               # ppb 보정량
    t, offs, states, freqs = [], [], [], []
    integ = 0.0
    prev = None
    for k in range(n):
        meas = offset + rng.normal(0, 8)
        if k == 0:
            st = 0
        elif k == 1:
            st = 1
            # 두 샘플로 주파수 추정 후 step
            freq = -(meas - prev) + 400.0  # 주파수 추정에 400 ppb 오차가 남았다고 가정
            integ = freq
            offset = -1500.0 + rng.normal(0, 50)  # step 후 남은 오차(가정)
            meas = offset
        else:
            st = 2
            integ += -ki * meas
            freq = -kp * meas + integ
        t.append(k); offs.append(meas); states.append(st); freqs.append(freq)
        prev = meas
        offset = offset + (true_freq_err + freq) * 1.0  # 1 s 동안 쌓이는 ns
    return np.array(t), np.array(offs), np.array(states), np.array(freqs)


def servo_states() -> None:
    t, offs, st, _ = simulate()
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.set_yscale("symlog", linthresh=100)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:,.0f}"))
    for s, c, lab in [(0, COLORS[3], "s0: 미동기(주파수 추정 중)"), (1, COLORS[1], "s1: step"),
                      (2, COLORS[0], "s2: 잠김(PI 제어)")]:
        m = st == s
        ax.plot(t[m], offs[m], "o", color=c, ms=5, label=lab)
    ax.plot(t, offs, color=GRAY, lw=0.8, zorder=0)
    ax.axhline(0, color="black", lw=0.8)
    ax.axhspan(-100, 100, color="#F3F4F6", zorder=-1)
    ax.text(39, 60, "±100 ns", color=GRAY, fontsize=9, ha="right", va="center")
    ax.set_xlabel("ptp4l 로그 줄 (Sync 1 s 주기)")
    ax.set_ylabel("master offset [ns] (대칭 로그)")
    ax.set_title("ptp4l 서보 상태와 수렴 (모의 개념도, 값은 가정)")
    ax.legend(loc="lower right")
    _save(fig, "servo-states")


if __name__ == "__main__":
    setup()
    servo_states()
