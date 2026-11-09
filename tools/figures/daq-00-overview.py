import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
import numpy as np
from _style import setup, save, COLORS, GRAY

setup()
SLUG = "daq-00-overview"

# 일반적인 값으로 계산한 대역폭 예산 (필자 시스템 수치 아님)
MB = 1e6
raw_1080 = 1920 * 1080 * 2 * 30 / MB  # YUV 4:2:2(2 B/px), 30 fps
raw_4k = 3840 * 2160 * 2 * 30 / MB
items = [
    ("1080p30 무압축 1채널", raw_1080, COLORS[1]),
    ("1080p30 무압축 8채널", raw_1080 * 8, COLORS[1]),
    ("4K30 무압축 8채널", raw_4k * 8, COLORS[1]),
    ("1080p30 H.264 8채널\n(채널당 10 Mb/s)", 8 * 10e6 / 8 / MB, COLORS[0]),
    ("4K30 H.265 8채널\n(채널당 20 Mb/s)", 8 * 20e6 / 8 / MB, COLORS[0]),
]
fig, ax = plt.subplots(figsize=(8.2, 3.9))
y = np.arange(len(items))[::-1]
for yi, (label, v, c) in zip(y, items):
    ax.barh(yi, v, color=c, height=0.55)
    ax.text(v * 1.12, yi, f"{v:,.0f} MB/s", va="center", fontsize=10)
ax.set_yticks(y, [i[0] for i in items])
ax.set_xscale("log")
ax.set_xlim(3, 3e4)
refs = [(125, "1 GbE 선로 속도\n125 MB/s"), (500, "SATA SSD 순차 쓰기\n≈500 MB/s (일반적)")]
for (x, t), ha, k in zip(refs, ["right", "left"], [0.94, 1.06]):
    ax.axvline(x, color=GRAY, ls="--", lw=1)
    ax.text(x * k, y.max() + 0.5, t, fontsize=9, color=GRAY, va="bottom", ha=ha)
ax.set_ylim(-0.6, y.max() + 1.5)
ax.set_xlabel("데이터 속도 [MB/s] (로그 눈금)")
ax.grid(axis="y", visible=False)
ax.set_title("다채널 카메라 대역폭: 무압축과 카메라 단 압축 (일반 값으로 계산한 예)", loc="left")
save(fig, SLUG, "bandwidth-budget")
