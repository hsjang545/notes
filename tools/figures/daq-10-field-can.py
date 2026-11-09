import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from _style import setup, save, COLORS, GRAY

setup()
SLUG = "daq-10-field-can"

# 비트 하나 = 16 tq로 나눈 예에서 샘플 포인트 75 %와 87.5 %
tq = 16
fig, axes = plt.subplots(2, 1, figsize=(8.2, 3.3), sharex=True)
for ax, (sp, label) in zip(axes, [(12, "샘플 포인트 75 % (12/16 tq)"), (14, "샘플 포인트 87.5 % (14/16 tq)")]):
    segs = [(0, 1, "Sync", GRAY), (1, sp - 1, "Prop_Seg + Phase_Seg1", COLORS[0]), (sp, tq - sp, "Phase_Seg2", COLORS[4])]
    for x0, w, name, c in segs:
        ax.add_patch(plt.Rectangle((x0, 0), w, 1, color=c, alpha=0.9, ec="white"))
        ax.text(x0 + w / 2, 0.5, name if w > 1 else "S", ha="center", va="center", fontsize=9, color="white")
    ax.axvline(sp, color="black", lw=2)
    ax.text(sp + 0.12, 1.06, "여기서 비트 값을 읽는다", fontsize=9, va="bottom")
    ax.set_ylim(0, 1.4)
    ax.set_yticks([])
    ax.grid(False)
    ax.set_title(label, loc="left", fontsize=10)
axes[1].set_xlim(0, tq)
axes[1].set_xticks(range(0, tq + 1, 2))
axes[1].set_xlabel("시간 양자 tq (한 비트 = 16 tq 예시)")
fig.tight_layout()
save(fig, SLUG, "sample-point")
