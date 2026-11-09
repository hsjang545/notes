"""comm-03-lin-flexray 그림: LIN 스케줄 테이블 타임라인, FlexRay 통신 사이클과 사이클 다중화."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "comm-03-lin-flexray"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
BAUD = 19_200


def finish(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def ms(bits: float) -> float:
    return bits / BAUD * 1e3


def lin_schedule() -> None:
    # (프레임 ID, 응답 바이트 수 또는 None=응답 없음, 응답 주체)
    slots = [
        ("0x10", 4, "마스터 자신"),
        ("0x21", 8, "슬레이브 A"),
        ("0x30", None, "이벤트 트리거: 응답 없음"),
        ("0x22", 2, "슬레이브 B"),
        ("0x10", 4, "마스터 자신"),
        ("0x21", 8, "슬레이브 A"),
    ]
    slot_ms = 10.0
    header = ms(34)
    fig, ax = plt.subplots(figsize=(9.6, 3.0))
    for i, (fid, n, who) in enumerate(slots):
        t0 = i * slot_ms
        ax.add_patch(Rectangle((t0, 0), slot_ms, 1.4, facecolor="#F9FAFB", edgecolor="#D1D5DB", lw=0.8))
        ax.add_patch(Rectangle((t0, 0.2), header, 0.5, facecolor=COLORS[0], alpha=0.7, lw=0))
        if n:
            resp = ms(10 * (n + 1))
            ax.add_patch(Rectangle((t0 + header + 0.2, 0.2), resp, 0.5, facecolor=COLORS[2], alpha=0.7, lw=0))
        ax.text(t0 + 0.2, 0.95, f"ID {fid}", fontsize=8.5, va="center")
        ax.text(t0 + 0.2, 1.2, who, fontsize=7.5, va="center", color=GRAY)
    ax.add_patch(Rectangle((0.0, -0.75), 1.2, 0.35, facecolor=COLORS[0], alpha=0.7, lw=0))
    ax.text(1.5, -0.57, f"헤더: Break+Sync+PID 34비트 ≈ {header:.1f} ms", fontsize=8.5, va="center")
    ax.add_patch(Rectangle((22.0, -0.75), 1.2, 0.35, facecolor=COLORS[2], alpha=0.7, lw=0))
    ax.text(23.5, -0.57, f"응답: 10×(N+1)비트 (8바이트면 {ms(90):.1f} ms)", fontsize=8.5, va="center")
    ax.text(44.0, -0.57, "슬롯 10 ms (19.2 kbit/s, 헤더·응답 사이 간격 생략)", fontsize=8.5, va="center", color=GRAY)
    ax.set_xlim(-0.5, 60.5)
    ax.set_ylim(-1.0, 1.6)
    ax.set_yticks([])
    ax.set_xlabel("시간 (ms)")
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.set_title("LIN 스케줄 테이블: 마스터가 슬롯마다 헤더를 보내고, 해당 ID의 담당 노드가 응답한다", fontsize=11)
    finish(fig, "lin-schedule")


def flexray_cycle() -> None:
    n_static = 10
    static_ms = 0.3
    dyn_start = n_static * static_ms
    dyn_len = 1.4
    sw_len = 0.15
    nit_len = 0.45
    cycle = dyn_start + dyn_len + sw_len + nit_len
    fig, ax = plt.subplots(figsize=(9.6, 4.2))
    rows = 4
    for c in range(rows):
        y = (rows - 1 - c) * 1.0
        for s in range(n_static):
            x = s * static_ms
            color = COLORS[0]
            label = str(s + 1)
            if s == 2:   # 슬롯 3을 사이클 다중화: 짝수 사이클 A, 홀수 사이클 B
                color = COLORS[1] if c % 2 == 0 else COLORS[3]
                label = "3\nA" if c % 2 == 0 else "3\nB"
            ax.add_patch(Rectangle((x, y + 0.1), static_ms, 0.7, facecolor=color, alpha=0.55, edgecolor="white", lw=1.2))
            ax.text(x + static_ms / 2, y + 0.45, label, ha="center", va="center", fontsize=7.5)
        # 동적 세그먼트: 미니슬롯, 보낼 프레임이 있는 ID만 늘어남
        ax.add_patch(Rectangle((dyn_start, y + 0.1), dyn_len, 0.7, facecolor="#F3F4F6", edgecolor="#D1D5DB", lw=0.8))
        frames = [(0.0, 0.35, "11"), (0.45, 0.25, "14")] if c % 2 == 0 else [(0.15, 0.5, "12")]
        for off, w, fid in frames:
            ax.add_patch(Rectangle((dyn_start + off, y + 0.1), w, 0.7, facecolor=COLORS[2], alpha=0.6, lw=0))
            ax.text(dyn_start + off + w / 2, y + 0.45, fid, ha="center", va="center", fontsize=7.5)
        for k in range(28):
            xk = dyn_start + k * dyn_len / 28
            ax.plot([xk, xk], [y + 0.1, y + 0.2], color=GRAY, lw=0.5)
        ax.add_patch(Rectangle((dyn_start + dyn_len, y + 0.1), sw_len, 0.7, facecolor=COLORS[4], alpha=0.4, lw=0))
        ax.add_patch(Rectangle((dyn_start + dyn_len + sw_len, y + 0.1), nit_len, 0.7, facecolor="#D1D5DB", lw=0))
        ax.text(-0.08, y + 0.45, f"사이클 {c}", ha="right", va="center", fontsize=9)
    top = rows * 1.0
    for x0, x1, name in [
        (0, dyn_start, "정적 세그먼트 (고정 슬롯, TDMA)"),
        (dyn_start, dyn_start + dyn_len, "동적 세그먼트 (미니슬롯)"),
        (dyn_start + dyn_len, dyn_start + dyn_len + sw_len, "SW"),
        (dyn_start + dyn_len + sw_len, cycle, "NIT"),
    ]:
        ax.annotate("", xy=(x1, top + 0.05), xytext=(x0, top + 0.05), arrowprops=dict(arrowstyle="<->", color="#374151", lw=0.9))
        ax.text((x0 + x1) / 2, top + 0.12, name, ha="center", va="bottom", fontsize=8.5)
    ax.text(0, -0.35, "슬롯 3: 짝수 사이클은 신호 A, 홀수 사이클은 신호 B (베이스 사이클 0/1, 반복 2). "
            "동적 세그먼트의 숫자는 프레임 ID.", fontsize=8.5, color=GRAY)
    ax.set_xlim(-0.75, cycle + 0.05)
    ax.set_ylim(-0.6, top + 0.55)
    ax.axis("off")
    ax.set_title("FlexRay 통신 사이클 (예시 구성, 길이는 개념적인 비율)", fontsize=11, pad=4)
    finish(fig, "flexray-cycle")


if __name__ == "__main__":
    setup()
    lin_schedule()
    flexray_cycle()
