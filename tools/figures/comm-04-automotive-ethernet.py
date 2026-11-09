"""comm-04-automotive-ethernet 그림: 802.1Q 태그가 붙은 이더넷 프레임, SOME/IP 헤더 배치."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "comm-04-automotive-ethernet"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def finish(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def box(ax, x, y, w, h, text, color, fs=9, sub=None):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor="#374151", lw=0.8))
    ax.text(x + w / 2, y + h / 2 + (0.12 if sub else 0), text, ha="center", va="center", fontsize=fs)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.22, sub, ha="center", va="center", fontsize=7.5, color=GRAY)


def vlan_frame() -> None:
    fig, ax = plt.subplots(figsize=(9.6, 3.4))
    fields = [
        ("목적지 MAC", "6 B", 2.2, "#E5E7EB"),
        ("출발지 MAC", "6 B", 2.2, "#E5E7EB"),
        ("802.1Q 태그", "4 B", 2.0, "#FDE68A"),
        ("EtherType", "2 B", 1.4, "#E5E7EB"),
        ("페이로드 (IP·UDP·SOME/IP …)", "42~1500 B", 4.6, "#DBEAFE"),
        ("FCS", "4 B", 1.0, "#E5E7EB"),
    ]
    x = 0.0
    tag_x = 0.0
    for name, size, w, c in fields:
        box(ax, x, 1.6, w, 0.8, name, c, sub=size)
        if name.startswith("802.1Q"):
            tag_x = x
        x += w
    # 태그 확대
    sub = [("TPID 0x8100", "16비트", 3.2), ("PCP", "3", 1.3), ("DEI", "1", 0.9), ("VLAN ID (VID)", "12비트", 3.6)]
    sx = tag_x - 3.4
    total = sum(w for _, _, w in sub)
    ax.plot([tag_x, sx], [1.6, 0.9], color=GRAY, lw=0.8)
    ax.plot([tag_x + 2.0, sx + total], [1.6, 0.9], color=GRAY, lw=0.8)
    for name, bits, w in sub:
        box(ax, sx, 0.1, w, 0.8, name, "#FEF3C7", fs=8.5, sub=bits)
        sx += w
    ax.text(sx + 0.3, 0.5, "PCP: 우선순위 0~7 (스위치 큐 선택)\nDEI: 혼잡 시 먼저 버려도 되는 프레임\nVID: 1~4094 (0, 4095 예약)",
            ha="left", va="center", fontsize=8.5, color=GRAY)
    ax.set_xlim(-0.2, x + 1.2)
    ax.set_ylim(-0.1, 2.6)
    ax.axis("off")
    ax.set_title("802.1Q 태그가 붙은 이더넷 프레임 (프리앰블·SFD 제외)", fontsize=11)
    finish(fig, "vlan-frame")


def someip_header() -> None:
    """32비트 폭 행으로 그린 SOME/IP 헤더(빅 엔디언)."""
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    W = 8.0   # 32비트 = 8 단위
    rows = [
        [("Service ID", 16, COLORS[0]), ("Method ID (MSB=1이면 Event)", 16, COLORS[0])],
        [("Length (Request ID부터 끝까지의 바이트 수)", 32, COLORS[4])],
        [("Client ID", 16, COLORS[2]), ("Session ID", 16, COLORS[2])],
        [("Protocol Ver.\n0x01", 8, COLORS[3]), ("Interface Ver.", 8, COLORS[3]),
         ("Message Type", 8, COLORS[3]), ("Return Code", 8, COLORS[3])],
    ]
    labels = ["Message ID", "", "Request ID", ""]
    for r, fields in enumerate(rows):
        y = (len(rows) - r) * 0.8
        x = 0.0
        for name, bits, c in fields:
            w = W * bits / 32
            ax.add_patch(Rectangle((x, y), w, 0.8, facecolor=c, alpha=0.3, edgecolor="#374151", lw=0.8))
            ax.text(x + w / 2, y + 0.4, name, ha="center", va="center", fontsize=8.5)
            x += w
        ax.text(-0.15, y + 0.4, f"바이트 {4 * r}~{4 * r + 3}", ha="right", va="center", fontsize=8.5)
        if labels[r]:
            ax.text(W + 0.15, y + 0.4, f"← {labels[r]}", ha="left", va="center", fontsize=8.5, color=GRAY)
    ax.add_patch(Rectangle((0, -0.0), W, 0.8, facecolor="#F3F4F6", edgecolor="#374151", lw=0.8, ls="--"))
    ax.text(W / 2, 0.4, "Payload (서비스 정의에 따른 직렬화 데이터, 가변 길이)", ha="center", va="center", fontsize=8.5)
    for b in (0, 8, 16, 24, 32):
        ax.text(W * b / 32, len(rows) * 0.8 + 0.85, str(b), ha="center", va="bottom", fontsize=8, color=GRAY)
    ax.annotate("", xy=(W + 1.55, 0.0), xytext=(W + 1.55, 2.4),
                arrowprops=dict(arrowstyle="<->", color=COLORS[1], lw=1.2))
    ax.text(W + 1.7, 1.2, "Length가\n세는 범위", fontsize=8, color=COLORS[1], va="center")
    ax.set_xlim(-1.6, W + 3.4)
    ax.set_ylim(-0.2, len(rows) * 0.8 + 1.3)
    ax.axis("off")
    ax.set_title("SOME/IP 헤더 16바이트 (빅 엔디언, 위 숫자는 비트 위치)", fontsize=11)
    finish(fig, "someip-header")


if __name__ == "__main__":
    setup()
    vlan_frame()
    someip_header()
