"""sensor-10-selection 그림: 시야 커버리지 평면도, 근거리 사각, 필요 탐지 거리."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Wedge  # noqa: E402
import numpy as np  # noqa: E402

SLUG = "sensor-10-selection"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


CAR_L, CAR_W = 4.8, 1.9   # 차량 길이·폭 [m], 원점은 차량 중심


def car(ax: plt.Axes) -> None:
    ax.add_patch(Rectangle((-CAR_L / 2, -CAR_W / 2), CAR_L, CAR_W, color="#374151", zorder=5))
    ax.annotate("", (CAR_L / 2 + 0.8, 0), (CAR_L / 2 - 0.4, 0), zorder=6,
                arrowprops=dict(arrowstyle="->", color="white", lw=1.5))


def wedge(ax: plt.Axes, xy: tuple[float, float], r: float, center_deg: float, half_fov: float,
          color: str, alpha: float = 0.25, label: str | None = None) -> None:
    ax.add_patch(Wedge(xy, r, center_deg - half_fov, center_deg + half_fov, color=color, alpha=alpha, lw=0,
                       label=label))


def fov_coverage() -> None:
    """가상의 일반적 구성(예시): 실제 차량·제품 배치가 아니다."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.5, 1]})
    fx, rx = CAR_L / 2, -CAR_L / 2
    # 원거리 보기
    wedge(a1, (0, 0), 120, 0, 180, COLORS[2], 0.10, "루프 라이다 360°, 약 120 m")
    wedge(a1, (fx, 0), 250, 0, 9, COLORS[1], 0.30, "전방 레이더 ±9°, 약 250 m")
    wedge(a1, (fx - 2.5, 0), 150, 0, 30, COLORS[0], 0.25, "전방 카메라 60°, 약 150 m")
    for (x, y), c in (((fx, CAR_W / 2), 45), ((fx, -CAR_W / 2), -45), ((rx, CAR_W / 2), 135), ((rx, -CAR_W / 2), -135)):
        wedge(a1, (x, y), 80, c, 75, COLORS[3], 0.18)
    a1.add_patch(Wedge((0, 0), 1, 0, 1, color=COLORS[3], alpha=0.18, label="코너 레이더 ±75°, 약 80 m"))
    a1.set_xlim(-100, 260)
    a1.set_ylim(-130, 130)
    a1.set_title("원거리: 센서별 시야 겹침 (예시 구성)", loc="left", fontsize=10.5)
    a1.legend(loc="lower right", fontsize=8.5)
    # 근거리 보기
    wedge(a2, (0, 0), 20, 0, 180, COLORS[2], 0.10)
    a2.add_patch(plt.Circle((0, 0), 4.3, fill=False, ec=COLORS[2], ls="--", lw=1.5, hatch="///", alpha=0.6, zorder=3))
    a2.text(0, 4.6, "루프 라이다 지면 사각\n(높이 2 m, 최하단 −25° → 약 4.3 m)", ha="center", fontsize=8.5,
            color=COLORS[2], zorder=6)
    for (x, y), c in (((fx, 0), 0), ((rx, 0), 180), ((0, CAR_W / 2), 90), ((0, -CAR_W / 2), -90)):
        wedge(a2, (x, y), 8, c, 95, COLORS[0], 0.15)
    for side in (fx, rx):
        for y in np.linspace(-0.7, 0.7, 4):
            ang = 0 if side > 0 else 180
            wedge(a2, (side, y), 4.5, ang, 30, GRAY, 0.12)
    a2.text(fx + 4.6, -2.2, "초음파\n약 0.15~5 m", fontsize=8.5, color="black", zorder=6)
    a2.text(-1.0, -7.8, "서라운드 어안 4대(190° 안팎)", fontsize=8.5, color=COLORS[0], zorder=6)
    a2.set_xlim(-12, 12)
    a2.set_ylim(-10, 10)
    a2.set_title("근거리: 사각과 근접 센서", loc="left", fontsize=10.5)
    for ax in (a1, a2):
        car(ax)
        ax.set_aspect("equal")
        ax.set_xlabel("x [m] (전방)")
    a1.set_ylabel("y [m]")
    fig.tight_layout()
    out(fig, "fov-coverage")


def blind_radius() -> None:
    h = np.linspace(0.3, 2.5, 100)
    fig, ax = plt.subplots(figsize=(7.2, 4))
    for a, c in zip((15, 25, 40), COLORS):
        ax.plot(h, h / np.tan(np.radians(a)), color=c, lw=2, label=f"최하단 빔 −{a}°")
    ax.plot(2.0, 2.0 / np.tan(np.radians(25)), "o", color=COLORS[1])
    ax.annotate("h = 2 m, −25° → 약 4.3 m", (2.0, 4.29), (1.0, 7.0), fontsize=9.5,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.set_xlim(0.3, 2.5)
    ax.set_ylim(0, 10)
    ax.set_xlabel("장착 높이 h [m]")
    ax.set_ylabel("지면 사각 반경 [m]")
    ax.legend(loc="upper left")
    ax.set_title("수평 장착 센서의 근거리 지면 사각 r = h / tan α (차체 가림 제외)", loc="left", fontsize=11)
    out(fig, "blind-radius")


def required_distance() -> None:
    v_kmh = np.linspace(10, 130, 200)
    v = v_kmh / 3.6
    t_total, a = 0.5, 6.0
    d_react = v * t_total
    d_brake = v**2 / (2 * a)
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.stackplot(v_kmh, d_react, d_brake, colors=[COLORS[0], COLORS[1]], alpha=0.7,
                 labels=[f"인식·시스템 지연 구간 v·{t_total} s", f"제동 구간 v²/(2·{a:.0f} m/s²)"])
    ax.plot(60, 60 / 3.6 * t_total + (60 / 3.6) ** 2 / (2 * a), "o", color="black")
    ax.annotate("60 km/h: 약 31 m + 여유 거리", (60, 31.5), (30, 75), fontsize=9.5,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.set_xlim(10, 130)
    ax.set_ylim(0, 130)
    ax.set_xlabel("자차 속도 [km/h]")
    ax.set_ylabel("필요 탐지 거리 [m]")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("정지 물체 앞에서 멈추는 데 필요한 탐지 거리 (가정: 지연 0.5 s, 감속 6 m/s²)", loc="left", fontsize=10.5)
    out(fig, "required-distance")


if __name__ == "__main__":
    setup()
    fov_coverage()
    blind_radius()
    required_distance()
