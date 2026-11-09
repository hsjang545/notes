"""comm-09-data-formats 그림: 같은 Header 메시지의 CDR·Protobuf 바이트 배치, PCAP·MCAP 파일 구조."""

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "comm-09-data-formats"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
SEC, NSEC, FRAME = 1_762_646_400, 500_000_000, "lidar_top"


def finish(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def varint(v: int) -> bytes:
    out = bytearray()
    while True:
        b = v & 0x7F
        v >>= 7
        if v:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def cdr_segments() -> list[tuple[str, bytes, str]]:
    name = FRAME.encode() + b"\x00"
    return [
        ("캡슐화 헤더\n(CDR_LE)", b"\x00\x01\x00\x00", "#E5E7EB"),
        ("stamp.sec\nint32", struct.pack("<i", SEC), COLORS[0]),
        ("stamp.nanosec\nuint32", struct.pack("<I", NSEC), COLORS[5]),
        ("frame_id 길이\nuint32 (NUL 포함)", struct.pack("<I", len(name)), COLORS[4]),
        ("frame_id 문자 + NUL", name, COLORS[2]),
    ]


def pb_segments() -> list[tuple[str, bytes, str]]:
    # message Time { int64 sec = 1; int32 nanosec = 2; }  message Header { Time stamp = 1; string frame_id = 2; }
    inner = varint(1 << 3 | 0) + varint(SEC) + varint(2 << 3 | 0) + varint(NSEC)
    return [
        ("태그\n필드1 LEN", varint(1 << 3 | 2), "#E5E7EB"),
        ("길이", varint(len(inner)), "#E5E7EB"),
        ("태그\nsec", varint(1 << 3 | 0), "#D1D5DB"),
        ("sec\nvarint", varint(SEC), COLORS[0]),
        ("태그\nnanosec", varint(2 << 3 | 0), "#D1D5DB"),
        ("nanosec\nvarint", varint(NSEC), COLORS[5]),
        ("태그\n필드2 LEN", varint(2 << 3 | 2), "#D1D5DB"),
        ("길이", varint(len(FRAME)), COLORS[4]),
        ("frame_id 문자", FRAME.encode(), COLORS[2]),
    ]


def draw_row(ax, y: float, segs, title: str) -> int:
    x = 0
    for k, (label, data, c) in enumerate(segs):
        for i, b in enumerate(data):
            ax.add_patch(Rectangle((x + i, y), 1, 0.8, facecolor=c, alpha=0.35, edgecolor="white", lw=1))
            ax.text(x + i + 0.5, y + 0.4, f"{b:02x}", ha="center", va="center", fontsize=7.5, family="monospace")
        ly = y - 0.15 - (0.55 if k % 2 else 0.0)
        ax.plot([x + len(data) / 2] * 2, [y, ly + 0.05], color=GRAY, lw=0.6)
        ax.text(x + len(data) / 2, ly, label, ha="center", va="top", fontsize=7.5)
        x += len(data)
    ax.text(-0.5, y + 0.4, f"{title}\n{x}바이트", ha="right", va="center", fontsize=9)
    return x


def cdr_vs_protobuf() -> None:
    fig, ax = plt.subplots(figsize=(10.0, 4.4))
    n1 = draw_row(ax, 2.6, cdr_segments(), "CDR")
    n2 = draw_row(ax, 0.3, pb_segments(), "Protobuf")
    for k in range(0, max(n1, n2) + 1, 4):
        ax.text(k, 3.5, str(k), ha="center", fontsize=7, color=GRAY)
    ax.text(0, 3.85, f"같은 값: stamp = ({SEC}, {NSEC}), frame_id = \"{FRAME}\"   (위 회색 숫자는 바이트 오프셋)",
            fontsize=8.5, color="#374151")
    ax.set_xlim(-3.2, max(n1, n2) + 0.5)
    ax.set_ylim(-1.2, 4.1)
    ax.axis("off")
    finish(fig, "cdr-vs-protobuf")


if __name__ == "__main__":
    setup()
    cdr_vs_protobuf()
    print(b"".join(d for _, d, _ in pb_segments()).hex(" "))
