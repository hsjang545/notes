"""comm-07-serial 그림: UART 8N1 파형, NMEA 문장 구조, PPS 뒤 문장 출력 타임라인."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "comm-07-serial"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def finish(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def uart_waveform() -> None:
    byte = ord("$")   # 0x24
    data = [(byte >> i) & 1 for i in range(8)]   # LSB 먼저
    bits = [1, 1] + [0] + data + [1] + [1, 1]
    names = ["idle", "idle", "start"] + [f"D{i}" for i in range(8)] + ["stop", "idle", "idle"]
    fig, ax = plt.subplots(figsize=(9.2, 3.0))
    xs, ys = [], []
    for k, b in enumerate(bits):
        xs += [k, k + 1]
        ys += [b, b]
    ax.plot(xs, ys, color=COLORS[0], lw=2.2)
    for k, (b, n) in enumerate(zip(bits, names)):
        shade = {"start": COLORS[1], "stop": COLORS[2]}.get(n)
        if shade:
            ax.add_patch(Rectangle((k, -0.15), 1, 1.3, facecolor=shade, alpha=0.15, lw=0))
        elif n.startswith("D"):
            ax.add_patch(Rectangle((k, -0.15), 1, 1.3, facecolor=COLORS[4], alpha=0.10, lw=0))
        ax.text(k + 0.5, -0.38, n, ha="center", va="top", fontsize=8.5)
        if n != "idle":
            ax.text(k + 0.5, 1.22, str(b), ha="center", va="bottom", fontsize=9, color=GRAY)
            ax.plot([k + 0.5], [b], "v" if b else "^", color=COLORS[1], ms=5)
    ax.annotate("", xy=(13, -0.95), xytext=(2, -0.95), arrowprops=dict(arrowstyle="<->", color="#374151"))
    ax.text(7.5, -1.05, "10비트 = 1바이트 (115200 baud면 86.8 µs)", ha="center", va="top", fontsize=9)
    ax.text(15.2, 1.0, "1 (mark)", va="center", fontsize=8.5, color=GRAY)
    ax.text(15.2, 0.0, "0 (space)", va="center", fontsize=8.5, color=GRAY)
    ax.text(0, 1.75, "문자 '$' = 0x24 = 0010 0100₂ 를 8N1로 보낸 TTL 레벨 파형 (LSB부터). ▼▲는 비트 중앙의 샘플링 위치",
            fontsize=8.5, color="#374151")
    ax.set_xlim(-0.2, 17)
    ax.set_ylim(-1.5, 2.0)
    ax.axis("off")
    finish(fig, "uart-8n1")


def nmea_structure() -> None:
    parts = [
        ("$", "시작"), ("GP", "토커"), ("GGA", "문장 형식"), (",123519", "UTC 12:35:19"),
        (",4807.038,N", "위도 ddmm.mmm"), (",01131.000,E", "경도 dddmm.mmm"), (",1", "품질"),
        (",08", "위성 수"), (",0.9", "HDOP"), (",545.4,M", "고도"), (",46.9,M", "지오이드고"),
        (",,", "빈 필드"), ("*47", "체크섬"), ("\\r\\n", "끝"),
    ]
    fig, ax = plt.subplots(figsize=(10.0, 2.6))
    x = 0.0
    cw = 0.115
    for i, (txt, lab) in enumerate(parts):
        w = len(txt) * cw if txt != "\\r\\n" else 4 * cw
        c = COLORS[i % 6]
        ax.add_patch(Rectangle((x, 0.55), w, 0.5, facecolor=c, alpha=0.18, edgecolor=c, lw=1))
        ax.text(x + w / 2, 0.8, txt, ha="center", va="center", fontsize=10, family="monospace")
        ly = 0.32 if i % 2 == 0 else 0.08
        ax.plot([x + w / 2, x + w / 2], [0.55, ly + 0.12], color=c, lw=0.8)
        ax.text(x + w / 2, ly, lab, ha="center", va="center", fontsize=8, color="#374151")
        x += w
    ax.annotate("", xy=(x - 4 * cw - 3 * cw, 1.2), xytext=(cw, 1.2), arrowprops=dict(arrowstyle="<->", color=COLORS[1]))
    ax.text((x - 7 * cw) / 2, 1.27, "체크섬 범위: '$'와 '*' 사이 모든 문자의 XOR = 0x47", ha="center", va="bottom",
            fontsize=8.5, color=COLORS[1])
    ax.set_xlim(-0.1, x + 0.1)
    ax.set_ylim(-0.1, 1.55)
    ax.axis("off")
    finish(fig, "nmea-structure")


def sentence_timeline() -> None:
    # 1초 주기 출력 예: (문장, 바이트 수) — 길이는 전형적인 값
    sentences = [("GGA", 72), ("RMC", 70), ("GSA", 66), ("GSV", 70), ("GSV", 70), ("GSV", 70), ("VTG", 40)]
    fig, ax = plt.subplots(figsize=(9.0, 3.2))
    for row, (baud, label) in enumerate([(9600, "9600 baud"), (115200, "115200 baud")]):
        y = 1 - row
        t = 30.0   # PPS 뒤 수신기가 출력을 시작하기까지의 지연(예시)
        for i, (name, n) in enumerate(sentences):
            d = 10 * n / baud * 1e3
            ax.add_patch(Rectangle((t, y - 0.3), d, 0.6, facecolor=COLORS[i % 6], alpha=0.55, edgecolor="white", lw=0.8))
            if d > 25:
                ax.text(t + d / 2, y, name, ha="center", va="center", fontsize=8)
            t += d
        ax.text(t + 8, y, f"마지막 문장 끝 ≈ {t:.0f} ms", va="center", fontsize=8.5)
        ax.text(-10, y, label, ha="right", va="center", fontsize=9.5)
    ax.axvline(0, color=COLORS[1], lw=1.6)
    ax.text(0, 1.55, "PPS (측위 epoch)", ha="center", fontsize=9, color=COLORS[1])
    ax.text(15, -0.62, "PPS 뒤 출력 시작까지의 지연 30 ms와 문장 길이는 예시 값", fontsize=8, color=GRAY)
    ax.set_xlim(-110, 800)
    ax.set_ylim(-0.8, 1.8)
    ax.set_yticks([])
    ax.set_xlabel("PPS 뒤 시간 (ms)")
    ax.spines["left"].set_visible(False)
    ax.grid(axis="y", visible=False)
    ax.set_title("한 epoch의 NMEA 문장이 전부 도착하기까지 (8N1, 문장당 10 × 바이트 수 / 보레이트)", fontsize=11)
    finish(fig, "sentence-timeline")


if __name__ == "__main__":
    setup()
    uart_waveform()
    nmea_structure()
    sentence_timeline()
