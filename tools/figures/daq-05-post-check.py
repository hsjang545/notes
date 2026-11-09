import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
import numpy as np
from _style import setup, save, COLORS, GRAY

setup()
SLUG = "daq-05-post-check"

# 합성 데이터: 토픽별 수신율과 두 단계 임계값
rng = np.random.default_rng(3)
topics = [f"토픽 {chr(65 + i)}" for i in range(10)]
ratio = np.clip(rng.normal(0.985, 0.008, len(topics)), 0, 1.0)
ratio[3], ratio[6], ratio[8] = 0.82, 0.31, 0.0
warn, err = 0.9, 0.5
colors = [COLORS[2] if r >= warn else COLORS[4] if r >= err else COLORS[1] for r in ratio]
fig, ax = plt.subplots(figsize=(8.2, 3.8))
x = np.arange(len(topics))
ax.bar(x, ratio, color=colors, width=0.6)
for xi, r in zip(x, ratio):
    ax.text(xi, r + 0.02, "0건" if r == 0 else f"{r:.2f}", ha="center", fontsize=9)
ax.plot([-0.6, len(x) - 0.55], [warn, warn], color=COLORS[4], ls="--", lw=1)
ax.plot([-0.6, len(x) - 0.55], [err, err], color=COLORS[1], ls="--", lw=1)
ax.text(len(x) - 0.5, warn, "WARN 경계\n0.9", ha="left", va="center", fontsize=9, color=COLORS[4])
ax.text(len(x) - 0.5, err, "ERROR 경계\n0.5", ha="left", va="center", fontsize=9, color=COLORS[1])
ax.set_xticks(x, topics)
ax.set_xlim(-0.6, len(x) + 0.6)
ax.set_ylim(0, 1.12)
ax.set_ylabel("수신율 = 실제 개수 ÷ 기대 개수")
ax.grid(axis="x", visible=False)
ax.set_title("수신율 판정 예 (합성 데이터): 초록 OK, 주황 WARN, 빨강 ERROR", loc="left")
save(fig, SLUG, "ratio-threshold")
