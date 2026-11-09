import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from _style import setup, save, COLORS, GRAY

setup()
SLUG = "daq-01-compute-os"

# 개념도: 기본값(period 1 s, runtime 0.95 s)에서 CPU 하나를 독점하는 SCHED_FIFO 태스크
fig, ax = plt.subplots(figsize=(8.4, 2.8))
for k in range(3):
    t0 = k * 1.0
    ax.broken_barh([(t0, 0.95)], (1.1, 0.8), color=COLORS[1])
    ax.broken_barh([(t0 + 0.95, 0.05)], (0.0, 0.8), color=COLORS[2])
    ax.annotate("", xy=(t0 + 0.95, 2.1), xytext=(t0, 2.1),
                arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1))
    ax.text(t0 + 0.475, 2.2, "RT 실행 최대 0.95 s", ha="center", fontsize=9, color=GRAY)
ax.text(2.0, -0.45, "← 남는 0.05 s (기본 설정에서 RT가 막히는 구간)", fontsize=9, color=COLORS[2])
ax.set_yticks([1.5, 0.4], ["SCHED_FIFO 태스크\n(바쁜 루프)", "SCHED_OTHER\n태스크"])
ax.set_xlim(0, 3.05)
ax.set_ylim(-0.7, 2.6)
ax.set_xlabel("시간 [s]  (sched_rt_period_us = 1,000,000, sched_rt_runtime_us = 950,000 기본값)")
ax.grid(False)
ax.set_title("RT throttling 개념도: 같은 CPU의 다른 일은 주기마다 남는 시간에만 돈다", loc="left")
save(fig, SLUG, "rt-throttling")
