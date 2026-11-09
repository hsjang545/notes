import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
import numpy as np
from _style import setup, save, COLORS, GRAY

setup()
SLUG = "daq-06-fake-loss"

# 합성 데이터: GOP 30, 30 fps. 키프레임은 크고 도착 지연이 튄다.
rng = np.random.default_rng(7)
n, gop, fps = 150, 30, 30
t = np.arange(n) / fps
key = np.arange(n) % gop == 0
size_kb = np.where(key, rng.normal(380, 15, n), rng.normal(35, 8, n)).clip(5)
payload = 1400  # RTP 패킷 하나의 페이로드 [B] (MTU 1500 기준 대략)
packets = np.ceil(size_kb * 1000 / payload)
delay_ms = rng.normal(8, 2, n).clip(2) + np.where(key, rng.normal(110, 15, n), 0)

fig, axes = plt.subplots(2, 1, figsize=(8.4, 4.8), sharex=True)
axes[0].bar(t, size_kb, width=0.8 / fps, color=np.where(key, COLORS[1], COLORS[0]))
axes[0].set_ylabel("프레임 크기 [KB]")
axes[0].text(4.06, 330,
             f"키프레임 ≈ {size_kb[key].mean():.0f} KB\n→ RTP 패킷 약 {packets[key].mean():.0f}개",
             fontsize=9, color=COLORS[1], va="top")
axes[1].plot(t, delay_ms, ".-", color=COLORS[0], lw=0.8, ms=4, label="P 프레임")
axes[1].plot(t[key], delay_ms[key], "o", color=COLORS[1], ms=6, label="키프레임")
axes[1].axhline(100, color=GRAY, ls="--", lw=1)
axes[1].text(t[-1], 104, "100 ms", ha="right", fontsize=9, color=GRAY)
axes[1].set_ylabel("도착 지연 [ms]")
axes[1].set_xlabel("시간 [s]")
axes[1].set_ylim(0, 170)
axes[1].legend(loc="upper center", ncol=2, fontsize=9)
axes[0].grid(axis="x", visible=False)
axes[0].set_title("키프레임 버스트와 도착 지연 (합성 데이터, GOP 30 · 30 fps)", loc="left")
fig.tight_layout()
save(fig, SLUG, "keyframe-burst")
