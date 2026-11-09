import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
import numpy as np
from _style import setup, save, COLORS, GRAY

setup()
SLUG = "daq-04-recording"

# 1) 저장 장치 용량별 연속 녹화 가능 시간 (일반 데이터 속도)
sizes_tb = np.array([0.5, 1, 2, 4, 8])
rates = [(10, "10 MB/s (압축 영상 여러 채널)"), (50, "50 MB/s"), (200, "200 MB/s"), (1000, "1 GB/s (무압축 다채널)")]
fig, ax = plt.subplots(figsize=(7.6, 4.2))
for (r, label), c in zip(rates, COLORS):
    hours = sizes_tb * 1e12 / (r * 1e6) / 3600
    ax.plot(sizes_tb, hours, "o-", color=c, label=label)
    txt = f"{hours[-1]:.0f} h" if hours[-1] >= 10 else f"{hours[-1]:.1f} h"
    ax.text(sizes_tb[-1] * 1.1, hours[-1], txt, va="center", fontsize=9, color=c)
ax.set_xscale("log", base=2)
ax.set_yscale("log")
ax.set_xticks(sizes_tb, ["0.5", "1", "2", "4", "8"])
ax.set_xlim(0.42, 12)
ax.set_yticks([0.1, 1, 10, 100], ["0.1", "1", "10", "100"])
ax.minorticks_off()
ax.set_xlabel("저장 장치 용량 [TB] (1 TB = 10¹² B, 파일 시스템 여유분 제외 전)")
ax.set_ylabel("연속 녹화 가능 시간 [h]")
ax.legend(loc="upper left", fontsize=9)
ax.set_title("녹화 가능 시간 = 용량 ÷ 데이터 속도", loc="left")
save(fig, SLUG, "storage-hours")

# 2) GOP 버퍼: 녹화 시작이 GOP 중간이면 다음 키프레임까지 디코드할 수 없다
gop, n, start = 10, 32, 13
first_key = ((start + gop - 1) // gop) * gop
prev_key = (start // gop) * gop
fig, axes = plt.subplots(2, 1, figsize=(8.4, 3.4), sharex=True)
for ax, title, buffered in zip(axes, ["GOP 버퍼 없음", "직전 GOP를 버퍼에 들고 있다가 함께 기록"], [False, True]):
    for i in range(n):
        key = i % gop == 0
        rec = i >= (prev_key if buffered else start)
        decodable = rec and (buffered or i >= first_key)
        if decodable:
            color = COLORS[1] if key else COLORS[0]
        elif rec:
            color = "#FCA5A5"
        else:
            color = "#F3F4F6"
        ax.add_patch(plt.Rectangle((i, 0), 0.9, 1, color=color, ec=GRAY, lw=0.5))
        ax.text(i + 0.45, 0.5, "I" if key else "P", ha="center", va="center", fontsize=8,
                color="white" if decodable else GRAY)
    ax.axvline(start, color="black", lw=1.5)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.grid(False)
    ax.set_title(title, loc="left", fontsize=10)
axes[0].annotate("녹화 시작", xy=(start, 1.0), xytext=(start + 0.3, 1.12), fontsize=9,
                 annotation_clip=False)
axes[0].text(first_key + 0.2, 1.12, "← 빨강: 기록됐지만 디코드할 수 없는 프레임", fontsize=8,
             color="#B91C1C", va="bottom")
axes[1].set_xlim(0, n)
axes[1].set_xlabel("프레임 번호 (예시: GOP 10, 회색은 기록되지 않은 프레임)")
fig.tight_layout()
save(fig, SLUG, "gop-buffer")
