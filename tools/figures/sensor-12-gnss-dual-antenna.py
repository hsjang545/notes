"""sensor-12-gnss-dual-antenna 그림: 속도별 코스 각 오차, 기준선 길이별 헤딩 오차, 헤딩 오차가 만드는 횡방향 오차."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SLUG = "sensor-12-gnss-dual-antenna"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
SIGMA_V = 0.025 / 3.6   # 속도 오차 0.025 km/h RMS (한 상용 GNSS/INS의 RTK 조건 사양)
SIGMA_B = 0.003         # 듀얼 안테나 헤딩에 필요한 상대 위치 정밀도 약 3 mm (같은 제조사 매뉴얼)
DUAL_SPEC = 0.04        # 같은 제품 헤딩 사양 0.04° 1σ


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def course_vs_speed() -> None:
    v = np.logspace(np.log10(0.3), np.log10(40), 200)
    err = np.degrees(SIGMA_V / v)
    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    ax.plot(v * 3.6, err, color=COLORS[1], lw=2, label="안테나 1개: 속도 방향(코스)으로 구한 각, σv/v")
    ax.axhline(DUAL_SPEC, color=COLORS[0], lw=2, ls="--", label="안테나 2개: 헤딩 사양 0.04°(정지에도 유지)")
    ax.axvspan(0, 10, color=GRAY, alpha=0.12)
    ax.text(1.3, 1.5, "저속·정지 구간", fontsize=9, color=GRAY)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1, 150)
    ax.set_ylim(0.005, 3)
    ax.set_xticks([1, 3, 10, 30, 100], ["1", "3", "10", "30", "100"])
    ax.set_yticks([0.01, 0.1, 1], ["0.01°", "0.1°", "1°"])
    ax.set_xlabel("차량 속도 [km/h]")
    ax.set_ylabel("방향 오차(1σ)")
    ax.legend(fontsize=9, loc="upper right")
    ax.set_title("속도 벡터로 구한 방향은 느릴수록 나빠지고 정지하면 정의되지 않는다", loc="left", fontsize=11)
    out(fig, "course-vs-speed")


def heading_vs_baseline() -> None:
    L = np.linspace(0.3, 5, 200)
    err = np.degrees(SIGMA_B / L)
    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    ax.plot(L, err, color=COLORS[0], lw=2, label="GNSS 기준선만으로 근사: 3 mm / L")
    ax.plot(2.0, DUAL_SPEC, "D", color="black", ms=7, label="상용 GNSS/INS 사양(2 m, INS 결합 후)")
    ax.axvline(5, color=GRAY, ls=":", lw=1.2)
    ax.text(4.95, 0.45, "최대 권장\n간격 5 m", ha="right", fontsize=9, color=GRAY)
    for x in (0.5, 1, 2, 4):
        y = np.degrees(SIGMA_B / x)
        ax.annotate(f"{y:.2f}°", (x, y), textcoords="offset points", xytext=(6, 6), fontsize=9)
    ax.set_xlim(0, 5.3)
    ax.set_ylim(0, 0.6)
    ax.set_xlabel("두 안테나 간격(기준선 길이) L [m]")
    ax.set_ylabel("헤딩 오차 [°]")
    ax.legend(fontsize=9)
    ax.set_title("듀얼 안테나 헤딩 오차는 기준선 길이에 반비례한다", loc="left", fontsize=11)
    out(fig, "heading-vs-baseline")


def lateral_error() -> None:
    d = np.linspace(0, 100, 200)
    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    for dpsi, c in zip((0.04, 0.1, 0.5, 1.0), (COLORS[0], COLORS[2], COLORS[4], COLORS[1])):
        e = d * np.radians(dpsi) * 100
        ax.plot(d, e, color=c, lw=2, label=f"헤딩 오차 {dpsi}°")
    ax.axhline(10, color=GRAY, ls=":", lw=1.2)
    ax.text(1, 11.5, "10 cm", fontsize=9, color=GRAY)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("기준점에서 대상까지 거리 d [m]")
    ax.set_ylabel("횡방향 위치 오차 [cm]")
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("헤딩 오차 × 거리 = 횡방향 오차: 50 m 앞에서 0.5°는 약 44 cm", loc="left", fontsize=11)
    out(fig, "lateral-error")


if __name__ == "__main__":
    setup()
    course_vs_speed()
    heading_vs_baseline()
    lateral_error()
