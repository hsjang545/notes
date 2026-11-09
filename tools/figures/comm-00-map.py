"""comm-00-map 그림: 인터페이스 대역폭-케이블 길이 지도, 센서 데이터율과 링크 용량."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "comm-00-map"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def finish(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def interface_map() -> None:
    """가로: 케이블 길이(m), 세로: 대역폭(bit/s). 상자는 대표 범위(규격 최대치와 흔한 값 기준)."""
    # (이름, 길이 최소, 길이 최대, 대역폭 최소, 대역폭 최대, 색 인덱스, 글자 위치 (x, y) 또는 None=가운데)
    items = [
        ("LIN", 10, 40, 1e3, 20e3, 4, None),
        ("CAN", 20, 500, 125e3, 1e6, 0, (60, 250e3)),
        ("CAN FD\n(데이터 단계)", 10, 40, 2e6, 8e6, 0, (4.0, 4e6)),
        ("FlexRay", 10, 24, 2.5e6, 10e6, 3, (15.5, 18e6)),
        ("100BASE-T1", 5, 15, 100e6, 100e6, 2, None),
        ("1000BASE-T1", 5, 40, 1e9, 1e9, 2, None),
        ("일반 이더넷\n(1G~10G)", 30, 100, 1e9, 10e9, 5, None),
        ("GMSL·FPD-Link", 5, 15, 3e9, 13e9, 1, (8.7, 26e9)),
        ("MIPI CSI-2", 0.1, 0.3, 1e9, 20e9, 3, None),
        ("USB 3.x", 1, 5, 5e9, 20e9, 6, (2.2, 35e9)),
        ("RS-232", 2, 15, 9.6e3, 1e6, 4, None),
        ("RS-422", 50, 1200, 100e3, 10e6, 4, (400, 4e6)),
    ]
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    for name, l0, l1, b0, b1, ci, pos in items:
        # 한 값만 있는 경우에도 보이도록 세로로 조금 넓힌다
        lo, hi = (b0 / 1.25, b1 * 1.25) if b0 == b1 else (b0, b1)
        ax.add_patch(
            Rectangle((l0, lo), l1 - l0, hi - lo, facecolor=COLORS[ci] if ci != 6 else GRAY, alpha=0.22,
                      edgecolor=COLORS[ci] if ci != 6 else GRAY, lw=1.4)
        )
        gx, gy = pos if pos else ((l0 * l1) ** 0.5, (lo * hi) ** 0.5)
        ax.text(gx, gy, name, ha="center", va="center", fontsize=9.5, color="#111827")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.05, 3000)
    ax.set_ylim(5e2, 8e10)
    ax.set_xlabel("케이블 길이 (m, 로그)")
    ax.set_ylabel("대역폭 (bit/s, 로그)")
    ax.set_yticks([1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10])
    ax.set_yticklabels(["1k", "10k", "100k", "1M", "10M", "100M", "1G", "10G"])
    ax.set_xticks([0.1, 1, 10, 100, 1000])
    ax.set_xticklabels(["0.1", "1", "10", "100", "1000"])
    ax.set_title("차량·센서 인터페이스의 대역폭과 케이블 길이 (대표 범위)")
    ax.text(
        0.99, 0.01, "CAN·RS-422은 속도를 낮출수록 길어진다. 값은 대표값이며 부품·케이블마다 다르다.",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color=GRAY,
    )
    finish(fig, "bandwidth-vs-length")


def sensor_rates() -> None:
    """센서 출력 데이터율 범위와 링크 용량(세로선)."""
    sensors = [
        ("차량 신호(CAN)", 5e3, 300e3),
        ("GNSS(NMEA·UBX)", 5e3, 100e3),
        ("IMU", 30e3, 3e6),
        ("레이더 오브젝트", 50e3, 500e3),
        ("레이더 포인트", 2e6, 50e6),
        ("라이다 포인트", 20e6, 600e6),
        ("카메라 원시(대당)", 0.7e9, 6e9),
    ]
    links = [
        ("CAN 500k", 500e3),
        ("CAN FD 2M", 2e6),
        ("100BASE-T1", 100e6),
        ("1 GbE", 1e9),
        ("GMSL2", 6e9),
    ]
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    for i, (name, lo, hi) in enumerate(sensors):
        ax.barh(i, hi - lo, left=lo, height=0.55, color=COLORS[0], alpha=0.8)
    ax.set_yticks(range(len(sensors)))
    ax.set_yticklabels([s[0] for s in sensors])
    ax.invert_yaxis()
    for j, (name, v) in enumerate(links):
        ax.axvline(v, color=COLORS[1], lw=1.2, ls="--")
        ax.text(v, -0.75 - 0.35 * (j % 2), name, ha="center", va="bottom", fontsize=8.5, color=COLORS[1])
    ax.set_xscale("log")
    ax.set_xlim(2e3, 2e10)
    ax.set_ylim(len(sensors) - 0.4, -1.3)
    ax.set_xticks([1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10])
    ax.set_xticklabels(["10k", "100k", "1M", "10M", "100M", "1G", "10G"])
    ax.set_xlabel("데이터율 (bit/s, 로그)")
    ax.grid(axis="y", visible=False)
    ax.set_title("센서 출력 데이터율(대략의 범위)과 링크 용량", pad=22)
    finish(fig, "sensor-rates")


if __name__ == "__main__":
    setup()
    interface_map()
    sensor_rates()
