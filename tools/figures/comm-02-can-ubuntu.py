"""comm-02-can-ubuntu 그림: DBC 신호의 비트 배치(인텔·모토로라), USB 어댑터의 타임스탬프 계단 모식도."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "comm-02-can-ubuntu"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def finish(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def intel_bits(start: int, length: int) -> list[int]:
    """인텔(리틀 엔디언): 시작 비트가 LSB, 비트 번호가 1씩 증가."""
    return [start + i for i in range(length)]


def motorola_bits(start: int, length: int) -> list[int]:
    """모토로라(빅 엔디언, DBC 표기): 시작 비트가 MSB, 바이트 안에서 아래로, 다음 바이트의 비트 7로 이어짐."""
    bits = []
    b = start
    for _ in range(length):
        bits.append(b)
        b = b + 15 if b % 8 == 0 else b - 1
    return bits   # MSB → LSB 순서


def dbc_layout() -> None:
    signals = [
        ("Speed  0|16@1+", intel_bits(0, 16), COLORS[0], "intel"),
        ("YawRate  16|16@1-", intel_bits(16, 16), COLORS[2], "intel"),
        ("Counter  32|4@1+", intel_bits(32, 4), COLORS[4], "intel"),
        ("BE_Example  55|12@0+ (가상)", motorola_bits(55, 12), COLORS[3], "motorola"),
    ]
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    owner = {}
    for idx, (_, bits, _, kind) in enumerate(signals):
        lsb = bits[0] if kind == "intel" else bits[-1]
        msb = bits[-1] if kind == "intel" else bits[0]
        for b in bits:
            owner[b] = (idx, "LSB" if b == lsb else ("MSB" if b == msb else ""))
    for byte in range(8):
        for col in range(8):
            bit = byte * 8 + (7 - col)   # 왼쪽이 비트 7
            x, y = col, 7 - byte
            if bit in owner:
                idx, tag = owner[bit]
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor=signals[idx][2], alpha=0.35, edgecolor="white", lw=1.5))
                label = f"{bit}\n{tag}" if tag else str(bit)
            else:
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor="#F9FAFB", edgecolor="white", lw=1.5))
                label = str(bit)
            ax.text(x + 0.5, y + 0.5, label, ha="center", va="center", fontsize=8,
                    color="#111827" if bit in owner else "#9CA3AF")
    for byte in range(8):
        ax.text(-0.2, 7 - byte + 0.5, f"바이트 {byte}", ha="right", va="center", fontsize=9)
    for col in range(8):
        ax.text(col + 0.5, 8.15, f"b{7 - col}", ha="center", va="bottom", fontsize=8.5, color=GRAY)
    # 범례
    for i, (name, _, c, kind) in enumerate(signals):
        y = 7.2 - i * 0.9
        ax.add_patch(Rectangle((8.6, y), 0.45, 0.45, facecolor=c, alpha=0.5, lw=0))
        desc = "인텔: 시작 비트 = LSB" if kind == "intel" else "모토로라: 시작 비트 = MSB"
        ax.text(9.2, y + 0.22, f"{name}\n{desc}", va="center", fontsize=8.5)
    ax.set_xlim(-1.8, 14.5)
    ax.set_ylim(-0.2, 8.8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("DBC 신호의 비트 배치 (8바이트 데이터, 각 칸의 숫자는 DBC 비트 번호)", fontsize=11)
    finish(fig, "dbc-bit-layout")


def timestamp_staircase() -> None:
    """모식도: 1 ms 주기 프레임을 USB 어댑터가 몇 개씩 묶어 올리면 소프트웨어 시각이 계단이 된다."""
    n = 24
    hw = np.arange(n) * 1.0                       # 버스 위 수신 시각(ms), 하드웨어 타임스탬프
    batch = 4
    sw = np.array([(k // batch + 1) * batch * 1.0 + 0.4 + 0.15 * (k % batch) for k in range(n)])
    fig, ax = plt.subplots(figsize=(8.0, 4.0))
    ax.plot(hw, hw, "o", color=COLORS[0], ms=5, label="하드웨어 타임스탬프 (컨트롤러가 수신 순간에 찍음)")
    ax.plot(hw, sw, "s", color=COLORS[1], ms=5, label="커널 소프트웨어 타임스탬프 (USB 전송 단위로 도착)")
    ax.plot([0, n], [0, n], color=GRAY, lw=0.8, ls="--")
    ax.set_xlabel("프레임이 버스에서 끝난 시각 (ms)")
    ax.set_ylabel("기록된 시각 (ms)")
    ax.set_xlim(-0.5, n)
    ax.set_ylim(-0.5, n + 5)
    ax.legend(loc="upper left", fontsize=9)
    ax.text(n - 0.5, 1.0, "모식도: 1 ms 주기 프레임을 4개씩 묶어 올리는 어댑터를 가정한 그림이며 측정값이 아니다.",
            ha="right", fontsize=8, color=GRAY)
    finish(fig, "timestamp-staircase")


if __name__ == "__main__":
    setup()
    dbc_layout()
    timestamp_staircase()
