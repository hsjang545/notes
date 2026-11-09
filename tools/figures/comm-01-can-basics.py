"""comm-01-can-basics 그림: 프레임 필드 배치, 비트 단위 중재, 비트 타이밍, 페이로드별 프레임 시간."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "comm-01-can-basics"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def finish(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def draw_fields(ax, y: float, fields, h: float = 0.8) -> float:
    """fields: (이름, 비트 수 문자열, 폭, 색). 왼쪽부터 상자를 그리고 끝 x를 돌려준다."""
    x = 0.0
    for name, bits, w, color in fields:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor="#374151", lw=0.8))
        vertical = w < 1.6
        ax.text(x + w / 2, y + h / 2, name, ha="center", va="center", fontsize=8.5,
                rotation=90 if vertical else 0)
        ax.text(x + w / 2, y - 0.12, bits, ha="center", va="top", fontsize=7.5, color=GRAY)
        x += w
    return x


def frame_layout() -> None:
    arb = "#DBEAFE"   # 중재 구간
    ctl = "#E5E7EB"
    dat = "#FDE68A"
    crc = "#FBCFE8"
    tail = "#F3F4F6"
    fast = "#FED7AA"  # FD 데이터 단계
    classic = [
        ("SOF", "1", 0.9, ctl), ("ID", "11", 3.6, arb), ("RTR", "1", 0.9, arb),
        ("IDE", "1", 0.9, ctl), ("r0", "1", 0.9, ctl), ("DLC", "4", 1.7, ctl),
        ("Data", "0~64", 6.0, dat), ("CRC", "15", 3.0, crc), ("CRC del", "1", 0.9, tail),
        ("ACK", "1", 0.9, tail), ("ACK del", "1", 0.9, tail), ("EOF", "7", 2.2, tail),
        ("IFS", "3", 1.4, tail),
    ]
    fd = [
        ("SOF", "1", 0.9, ctl), ("ID", "11", 3.6, arb), ("RRS", "1", 0.9, arb),
        ("IDE", "1", 0.9, ctl), ("FDF", "1", 0.9, ctl), ("res", "1", 0.9, ctl),
        ("BRS", "1", 0.9, ctl), ("ESI", "1", 0.9, fast), ("DLC", "4", 1.7, fast),
        ("Data", "0~512", 6.0, fast), ("SC", "4", 1.0, fast), ("CRC", "17/21", 2.1, fast),
        ("CRC del", "1", 0.9, tail), ("ACK", "1", 0.9, tail), ("ACK del", "1", 0.9, tail),
        ("EOF", "7", 2.2, tail), ("IFS", "3", 1.4, tail),
    ]
    fig, ax = plt.subplots(figsize=(9.6, 3.6))
    draw_fields(ax, 2.0, classic)
    draw_fields(ax, 0.2, fd)
    ax.text(-0.3, 2.4, "CAN classic\n(표준 ID)", ha="right", va="center", fontsize=9.5)
    ax.text(-0.3, 0.6, "CAN FD\n(표준 ID)", ha="right", va="center", fontsize=9.5)
    # BRS 샘플 포인트 ~ CRC 구분자 샘플 포인트가 데이터 비트레이트 구간
    x_brs = 0.9 + 3.6 + 0.9 + 0.9 + 0.9 + 0.9 + 0.9 * 0.75
    x_del = x_brs - 0.9 * 0.75 + 0.9 + 0.9 + 1.7 + 6.0 + 1.0 + 2.1 + 0.9 * 0.75
    ax.annotate("", xy=(x_del, 1.25), xytext=(x_brs, 1.25),
                arrowprops=dict(arrowstyle="<->", color=COLORS[1], lw=1.4))
    ax.text((x_brs + x_del) / 2, 1.33, "데이터 비트레이트 구간 (BRS 샘플 포인트 ~ CRC 구분자 샘플 포인트)",
            ha="center", va="bottom", fontsize=8.5, color=COLORS[1])
    ax.text(0.0, 3.05, "아래 회색 숫자는 비트 수. 스터프 비트는 표시하지 않음. 상자 폭은 비트 수에 비례하지 않음.",
            fontsize=8, color=GRAY, va="bottom")
    ax.set_xlim(-3.2, 30.5)
    ax.set_ylim(-0.4, 3.4)
    ax.axis("off")
    finish(fig, "frame-layout")


def id_bits(v: int) -> list[int]:
    return [(v >> (10 - i)) & 1 for i in range(11)]


def arbitration() -> None:
    nodes = [("노드 A (0x123)", 0x123), ("노드 B (0x125)", 0x125), ("노드 C (0x1A0)", 0x1A0)]
    seqs = {name: [0] + id_bits(v) for name, v in nodes}   # SOF + ID 11비트
    n = 12
    # 진 시점 계산: 자신이 1을 냈는데 버스가 0이면 그 비트에서 패배
    bus = []
    active = {name: True for name, _ in nodes}
    lost_at = {}
    for k in range(n):
        sent = {name: seqs[name][k] for name, _ in nodes if active[name]}
        b = min(sent.values())
        bus.append(b)
        for name, bit in sent.items():
            if bit == 1 and b == 0:
                active[name] = False
                lost_at[name] = k
    fig, ax = plt.subplots(figsize=(9.0, 4.2))
    rows = [name for name, _ in nodes] + ["버스 (와이어드 AND)"]
    for r, name in enumerate(rows):
        y0 = (len(rows) - 1 - r) * 1.6
        levels = bus if r == len(nodes) else seqs[name]
        stop = lost_at.get(name, n) if r < len(nodes) else n
        xs, ys = [], []
        for k in range(n):
            lvl = levels[k]
            xs += [k, k + 1]
            ys += [y0 + lvl, y0 + lvl]
        xs, ys = np.array(xs), np.array(ys)
        color = COLORS[2] if r == len(nodes) else COLORS[0]
        # 송신 구간(실선)과 패배 후(수신 전환, 점선 회색)
        cut = 2 * min(stop + 1, n) if stop < n else 2 * n
        ax.plot(xs[:cut + 1], ys[:cut + 1], color=color, lw=2)
        if stop < n:
            if cut < len(xs):
                ax.plot(xs[cut:], [y0 + 1] * (len(xs) - cut), color=GRAY, lw=1.2, ls=":")
            ax.text(stop + 1.1, y0 + 1.15, "중재 패배 → 수신으로 전환", fontsize=8.5, color=COLORS[1])
            ax.add_patch(Rectangle((stop, y0 - 0.1), 1, 1.2, facecolor=COLORS[1], alpha=0.15, lw=0))
        ax.text(-0.3, y0 + 0.5, name, ha="right", va="center", fontsize=9.5)
        for k in range(min(stop + 1, n) if r < len(nodes) else n):
            ax.text(k + 0.5, y0 + 0.5, str(levels[k]), ha="center", va="center", fontsize=8, color=GRAY)
    for k in range(n + 1):
        ax.axvline(k, color="#E5E7EB", lw=0.6, zorder=0)
    labels = ["SOF"] + [f"ID{10 - i}" for i in range(11)]
    for k, lab in enumerate(labels):
        ax.text(k + 0.5, -0.45, lab, ha="center", va="top", fontsize=7.5, rotation=0)
    ax.text(n + 0.1, 0.0, "0 = 우성", fontsize=8, va="center", color=GRAY)
    ax.text(n + 0.1, 1.0, "1 = 열성", fontsize=8, va="center", color=GRAY)
    ax.set_xlim(-3.6, n + 1.6)
    ax.set_ylim(-1.0, len(rows) * 1.6)
    ax.axis("off")
    ax.set_title("비트 단위 중재: 열성(1)을 냈는데 버스가 우성(0)이면 그 자리에서 물러난다", fontsize=11)
    finish(fig, "arbitration")


def bit_timing() -> None:
    segs = [("Sync", 1, "#9CA3AF"), ("Prop_Seg", 6, COLORS[5]), ("Phase_Seg1", 7, COLORS[0]), ("Phase_Seg2", 2, COLORS[4])]
    fig, ax = plt.subplots(figsize=(9.0, 2.8))
    x = 0
    for name, n, c in segs:
        for k in range(n):
            ax.add_patch(Rectangle((x + k, 0), 1, 1, facecolor=c, alpha=0.35, edgecolor="white", lw=1.2))
        ax.text(x + n / 2, 0.5, f"{name}\n{n} tq", ha="center", va="center", fontsize=9)
        x += n
    sp = 14
    ax.annotate("샘플 포인트\n14/16 = 87.5 %", xy=(sp, 1.0), xytext=(sp, 1.75), ha="center", fontsize=9.5,
                color=COLORS[1], arrowprops=dict(arrowstyle="->", color=COLORS[1], lw=1.5))
    ax.axvline(sp, ymin=0.18, ymax=0.62, color=COLORS[1], lw=1.5)
    ax.annotate("", xy=(16, -0.35), xytext=(0, -0.35), arrowprops=dict(arrowstyle="<->", color="#374151"))
    ax.text(8, -0.45, "1비트 = 16 tq × 125 ns = 2 µs  →  500 kbit/s (80 MHz ÷ prescaler 10)", ha="center", va="top",
            fontsize=9)
    ax.annotate("SJW만큼\n늘어날 수 있음", xy=(14, 0.05), xytext=(10.3, -1.35), fontsize=8, color=GRAY,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.annotate("SJW만큼\n줄어들 수 있음", xy=(15.5, 0.05), xytext=(16.4, -1.35), fontsize=8, color=GRAY,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.set_xlim(-0.5, 18.5)
    ax.set_ylim(-1.6, 2.4)
    ax.axis("off")
    finish(fig, "bit-timing")


def classic_bits(n: int, worst: bool) -> int:
    """IFS 포함 표준 ID classic 프레임 비트 수(Davis 등 2007)."""
    base = 8 * n + 47
    return base + ((34 + 8 * n - 1) // 4 if worst else 0)


def fd_bits(n: int, worst: bool) -> tuple[int, int]:
    """표준 ID CAN FD 프레임의 (중재 비트레이트 비트 수, 데이터 비트레이트 비트 수) 근사.

    중재 쪽: SOF~BRS 17비트 + CRC 구분자·ACK·ACK 구분자·EOF·IFS 13비트(+ 앞부분 동적 스터프 최대 4).
    데이터 쪽: ESI 1 + DLC 4 + 데이터 + 스터프 카운트 4 + CRC 17/21 + 고정 스터프 6/7 (+ 동적 스터프).
    """
    crc = 17 if n <= 16 else 21
    fsb = 6 if n <= 16 else 7
    nom = 30
    data = 5 + 8 * n + 4 + crc + fsb
    if worst:
        dyn = (17 + 5 + 8 * n - 1) // 4   # SOF~데이터 끝 동적 스터핑 최악
        nom += 4
        data += dyn - 4
    return nom, data


def frame_time() -> None:
    payload = np.arange(0, 65)
    fd_len = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]
    fig, ax = plt.subplots(figsize=(8.2, 4.6))

    def classic_time(p: int, worst: bool) -> float:
        frames = max(1, -(-p // 8))
        last = p - 8 * (frames - 1)
        return ((frames - 1) * classic_bits(8, worst) + classic_bits(last, worst)) / 500e3 * 1e3

    def fd_time(p: int, worst: bool, rd: float) -> float:
        n = next(L for L in fd_len if L >= p)     # DLC 단계로 올림
        nom, dat = fd_bits(n, worst)
        return nom / 500e3 * 1e3 + dat / rd * 1e3

    series = [
        ("CAN classic 500 kbit/s (8바이트씩 나눠 전송)", lambda p, w: classic_time(p, w), COLORS[0]),
        ("CAN FD 500 kbit/s / 2 Mbit/s", lambda p, w: fd_time(p, w, 2e6), COLORS[1]),
        ("CAN FD 500 kbit/s / 5 Mbit/s", lambda p, w: fd_time(p, w, 5e6), COLORS[2]),
    ]
    for label, f, c in series:
        lo = [f(int(p), False) for p in payload]
        hi = [f(int(p), True) for p in payload]
        ax.fill_between(payload, lo, hi, step="post", color=c, alpha=0.2, lw=0)
        ax.step(payload, hi, where="post", color=c, lw=1.8, label=label)
    ax.set_xlabel("보낼 데이터 (바이트)")
    ax.set_ylabel("버스 점유 시간 (ms)")
    ax.set_xlim(0, 64)
    ax.set_ylim(0, 2.4)
    ax.set_xticks([0, 8, 16, 24, 32, 48, 64])
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("데이터 양에 따른 버스 점유 시간 (선: 스터핑 최악, 띠 아래쪽: 스터핑 없음)", fontsize=11)
    ax.text(63, 0.62, "CAN FD는 DLC 단계(12, 16, 20, 24, 32, 48, 64바이트)로 올림. 필드별 비트 수로 센 근사.",
            ha="right", va="bottom", fontsize=8, color=GRAY)
    finish(fig, "frame-time")


if __name__ == "__main__":
    setup()
    frame_layout()
    arbitration()
    bit_timing()
    frame_time()
    for n in (8, 64):
        print("FD bits (no stuff / worst):", n, fd_bits(n, False), fd_bits(n, True))
