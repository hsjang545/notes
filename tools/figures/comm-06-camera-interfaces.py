"""comm-06-camera-interfaces 그림: 영상 데이터율과 링크 용량, CSI-2 패킷 구조, 노출에서 V4L2 타임스탬프까지."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "comm-06-camera-interfaces"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def finish(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def rates_vs_links() -> None:
    cams = [
        ("1080p30 RAW12", 1920 * 1080 * 30 * 12),
        ("1080p30 YUV422", 1920 * 1080 * 30 * 16),
        ("4K30 RAW12", 3840 * 2160 * 30 * 12),
        ("4K60 RAW12", 3840 * 2160 * 60 * 12),
    ]
    links = [
        ("USB3 Vision 실효(약 3 Gbit/s)", 3.2e9, COLORS[3]),
        ("1 GbE (GigE Vision)", 1e9, COLORS[5]),
        ("FPD-Link III (4.16 Gbit/s)", 4.16e9, COLORS[2]),
        ("GMSL2 (6 Gbit/s)", 6e9, COLORS[1]),
        ("FPD-Link IV 카메라 (7.55 Gbit/s)", 7.55e9, COLORS[4]),
        ("GMSL3 (12 Gbit/s)", 12e9, COLORS[6]),
    ]
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    ys = range(len(cams))
    ax.barh(list(ys), [v / 1e9 for _, v in cams], height=0.55, color=COLORS[0], alpha=0.85)
    for y, (name, v) in zip(ys, cams):
        ax.text(v / 1e9 + 0.12, y, f"{v / 1e9:.2f}", va="center", fontsize=9)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([n for n, _ in cams])
    ax.invert_yaxis()
    for i, (name, v, c) in enumerate(links):
        ax.axvline(v / 1e9, color=c, lw=1.4, ls="--", label=name)
    ax.legend(loc="lower right", fontsize=8.5, title="링크 용량(순방향)", title_fontsize=9, framealpha=1, frameon=True)
    ax.set_xlim(0, 13)
    ax.set_ylim(len(cams) - 0.4, -0.6)
    ax.set_xlabel("원시 영상 데이터율 (Gbit/s, 블랭킹·프로토콜 오버헤드 제외)")
    ax.grid(axis="y", visible=False)
    finish(fig, "rates-vs-links")


def csi2_packets() -> None:
    fig, ax = plt.subplots(figsize=(9.6, 3.6))

    def seq(y, fields, title):
        x = 0.0
        for name, sub, w, c in fields:
            ax.add_patch(Rectangle((x, y), w, 0.75, facecolor=c, edgecolor="#374151", lw=0.8))
            ax.text(x + w / 2, y + 0.47, name, ha="center", va="center", fontsize=8.5)
            ax.text(x + w / 2, y + 0.18, sub, ha="center", va="center", fontsize=7.5, color=GRAY)
            x += w
        ax.text(-0.2, y + 0.37, title, ha="right", va="center", fontsize=9.5)
        return x

    di = "#DBEAFE"
    seq(2.0, [("DI", "VC + DT", 1.6, di), ("16비트 데이터", "프레임 번호 등", 2.4, "#E5E7EB"), ("ECC", "8비트", 1.2, "#FBCFE8")],
        "짧은 패킷\n(FS, FE, LS, LE)")
    seq(0.8, [("DI", "VC + DT", 1.6, di), ("워드 수", "16비트", 1.6, "#E5E7EB"), ("ECC", "8비트", 1.2, "#FBCFE8"),
              ("페이로드: 한 줄의 픽셀", "워드 수만큼 (예: RAW12 1920픽셀 = 2880바이트)", 7.6, "#FDE68A"),
              ("CRC", "16비트", 1.2, "#FBCFE8")], "긴 패킷\n(픽셀 라인)")
    # 한 프레임의 순서
    order = [("FS", "#E5E7EB"), ("ED", "#C7D2FE"), ("라인 1", "#FDE68A"), ("라인 2", "#FDE68A"), ("…", "#FFFFFF"),
             ("라인 N", "#FDE68A"), ("FE", "#E5E7EB")]
    x = 0.0
    for name, c in order:
        w = 1.25
        ax.add_patch(Rectangle((x, -0.5), w, 0.6, facecolor=c, edgecolor="#374151", lw=0.8))
        ax.text(x + w / 2, -0.2, name, ha="center", va="center", fontsize=8.5)
        x += w + 0.15
    ax.text(-0.2, -0.2, "한 프레임", ha="right", va="center", fontsize=9.5)
    ax.text(x + 0.2, -0.2, "FS·FE: Frame Start·End (짧은 패킷), ED: 임베디드 데이터 라인(DT 0x12, 선택)",
            va="center", fontsize=8, color=GRAY)
    ax.text(0, 2.95, "DI(데이터 식별자) = 가상 채널(VC) + 데이터 타입(DT). 예: RAW10 0x2B, RAW12 0x2C, YUV422 8비트 0x1E",
            fontsize=8.5, color=GRAY)
    ax.set_xlim(-2.4, 16.5)
    ax.set_ylim(-0.7, 3.2)
    ax.axis("off")
    finish(fig, "csi2-packets")


def exposure_timeline() -> None:
    exp = 10.0      # 노출 시간 ms
    readout = 15.0  # 첫 행~마지막 행 판독 시작 차(롤링 셔터)
    xfer = 3.0      # 전송·드라이버 처리
    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    ax.add_patch(Polygon([[0, 3], [exp, 3], [exp + readout, 0], [readout, 0]], closed=True,
                         facecolor=COLORS[0], alpha=0.25, edgecolor=COLORS[0]))
    ax.plot([exp, exp + readout], [3, 0], color=COLORS[1], lw=2)
    ax.text(exp / 2 + 3, 2.6, "노출 (행마다 시작이 조금씩 늦음)", fontsize=9, color="#1F2937")
    ax.text(exp + readout / 2 + 1.4, 1.75, "판독", fontsize=9, color=COLORS[1])
    ax.text(-0.4, 3, "첫 행", ha="right", va="center", fontsize=9)
    ax.text(-0.4, 0, "마지막 행", ha="right", va="center", fontsize=9)
    marks = [
        (0, "트리거·첫 행\n노출 시작 (SOE)", COLORS[2]),
        (exp / 2 + readout / 2, "프레임 중앙 행의\n노출 중간", COLORS[3]),
        (exp + readout, "마지막 행\n판독 끝", COLORS[1]),
        (exp + readout + xfer, "V4L2 타임스탬프\n(EOF, 수신 완료)", COLORS[6]),
    ]
    aligns = ["center", "center", "right", "left"]
    for (t, lab, c), ha in zip(marks, aligns):
        ax.axvline(t, color=c, lw=1.4, ls="--", ymin=0.28, ymax=0.88)
        dx = {"center": 0, "right": -0.3, "left": 0.3}[ha]
        ax.text(t + dx, -0.95, lab, ha=ha, va="top", fontsize=8.5, color=c)
    t_mid = exp / 2 + readout / 2
    t_eof = exp + readout + xfer
    ax.annotate("", xy=(t_eof, 3.55), xytext=(t_mid, 3.55), arrowprops=dict(arrowstyle="<->", color="#374151"))
    ax.text((t_mid + t_eof) / 2, 3.65, f"{t_eof - t_mid:.1f} ms = 노출/2 + 판독/2 + 전송·처리",
            ha="center", va="bottom", fontsize=9)
    ax.set_xlim(-6, 36)
    ax.set_ylim(-2.4, 4.3)
    ax.set_yticks([])
    ax.set_xlabel("시간 (ms)  —  예시 값: 노출 10 ms, 롤링 셔터 판독 15 ms, 전송·처리 3 ms")
    ax.spines["left"].set_visible(False)
    ax.grid(axis="y", visible=False)
    finish(fig, "exposure-timeline")


if __name__ == "__main__":
    setup()
    rates_vs_links()
    csi2_packets()
    exposure_timeline()
