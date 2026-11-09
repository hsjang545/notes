import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
import numpy as np
from _style import setup, save, COLORS, GRAY

setup()
SLUG = "daq-08-extract"

# 합성 데이터: 기준 25 Hz, 대상 30 Hz(3 ms 어긋남, 중간에 끊김), 허용 오차 = 대상 주기의 절반
ref = np.arange(0.0, 0.40, 1 / 25)
tgt = np.arange(0.003, 0.40, 1 / 30)
tgt = tgt[(tgt < 0.17) | (tgt > 0.27)]
tol = 0.5 / 30


def nearest_match(ref_t: np.ndarray, tgt_t: np.ndarray, tol: float) -> np.ndarray:
    """본문 코드와 같은 함수."""
    idx = np.searchsorted(tgt_t, ref_t)
    left = np.clip(idx - 1, 0, tgt_t.size - 1)
    right = np.clip(idx, 0, tgt_t.size - 1)
    pick = np.where(np.abs(tgt_t[left] - ref_t) <= np.abs(tgt_t[right] - ref_t), left, right)
    pick[np.abs(tgt_t[pick] - ref_t) > tol] = -1
    return pick


m = nearest_match(ref, tgt, tol)
ms = 1e3
fig, ax = plt.subplots(figsize=(8.6, 3.0))
ax.axvspan(170, 270, color="#F3F4F6", lw=0)
ax.text(220, -0.38, "대상 샘플이 끊긴 구간", ha="center", fontsize=8, color=GRAY)
for r, j in zip(ref, m):
    ax.add_patch(plt.Rectangle(((r - tol) * ms, 0.88), 2 * tol * ms, 0.24, color=COLORS[5], alpha=0.3, lw=0))
    if j >= 0:
        ax.plot([r * ms, tgt[j] * ms], [1, 0], color=COLORS[2], lw=1.2)
    else:
        ax.text(r * ms, 0.5, "매칭\n없음", ha="center", va="center", fontsize=8, color=COLORS[1])
ax.plot(ref * ms, np.ones_like(ref), "s", color=COLORS[0], ms=7, label="기준 센서 25 Hz")
ax.plot(tgt * ms, np.zeros_like(tgt), "o", color=COLORS[1], ms=6, label="대상 센서 30 Hz")
ax.set_yticks([1, 0], ["기준", "대상"])
ax.set_ylim(-0.55, 1.35)
ax.set_xlim(-25, 400)
ax.set_xlabel("시간 [ms]  (하늘색 띠: 기준 시각 ± 허용 오차 16.7 ms)")
ax.grid(False)
ax.legend(loc="lower center", ncol=2, fontsize=9, bbox_to_anchor=(0.5, 1.0))
save(fig, SLUG, "nearest-match")
