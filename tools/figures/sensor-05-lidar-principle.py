"""sensor-05-lidar-principle 그림: 스캔 패턴, 거리별 점 간격, walk error."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SLUG = "sensor-05-lidar-principle"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def scan_patterns() -> None:
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.2))
    # 1) 기계식 회전: 16채널, 비균일 수직 배치, 수평 0.4° 간격 일부 구간
    elev = np.concatenate([np.linspace(-15, -3, 5), np.linspace(-2, 2, 7), np.linspace(4, 10, 4)])
    az = np.arange(-30, 30, 1.2)
    A, E = np.meshgrid(az, elev)
    axes[0].plot(A.ravel(), E.ravel(), ".", ms=2.5, color=COLORS[0], rasterized=True)
    axes[0].set_title("기계식 회전\n(링 단위 격자, 지평선 근처 조밀)", fontsize=10)
    # 2) MEMS 래스터: 수평 공진 + 수직 느린 주사
    t = np.linspace(0, 1, 4000)
    x = 30 * np.sin(2 * np.pi * 20 * t)
    y = 12 * (2 * t - 1)
    axes[1].plot(x[::4], y[::4], ".", ms=1.5, color=COLORS[1], rasterized=True)
    axes[1].set_title("MEMS·폴리곤 래스터\n(지그재그 주사)", fontsize=10)
    # 3,4) 리슬리 프리즘: 두 쐐기의 편향 벡터 합(장미 무늬)
    for ax, t_end, title in ((axes[2], 0.1, "리슬리 프리즘 0.1 s\n(짧은 시간: 성김)"),
                             (axes[3], 1.0, "리슬리 프리즘 1 s 누적\n(누적할수록 조밀)")):
        tt = np.linspace(0, t_end, int(24000 * t_end))
        w1, w2 = 2 * np.pi * 70.3, -2 * np.pi * 49.1
        z = 0.5 * (np.exp(1j * w1 * tt) + np.exp(1j * w2 * tt)) * 30
        ax.plot(z.real, z.imag, ".", ms=0.8, color=COLORS[2], alpha=0.6, rasterized=True)
        ax.set_title(title, fontsize=10)
    for ax in axes:
        ax.set_aspect("equal")
        ax.set_xlim(-33, 33)
        ax.set_ylim(-33, 33)
        ax.set_xlabel("수평각 [°]", fontsize=9)
        ax.tick_params(labelsize=8)
    axes[0].set_ylabel("수직각 [°]", fontsize=9)
    fig.set_dpi(150)
    fig.suptitle("스캔 방식별 점 분포 (개념 모의, 실제 제품 패턴과 다름)", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    out(fig, "scan-patterns")


def point_spacing() -> None:
    r = np.linspace(0, 200, 400)
    fig, ax = plt.subplots(figsize=(7.5, 4))
    for deg, c in zip((0.1, 0.2, 0.4), COLORS):
        ax.plot(r, r * np.radians(deg), color=c, lw=2, label=f"각해상도 {deg}°")
    ax.axhline(0.5, color=GRAY, ls="--", lw=1)
    ax.text(3, 0.53, "보행자 폭 약 0.5 m", fontsize=9.5, color=GRAY)
    ax.axhline(0.25, color=GRAY, ls=":", lw=1)
    ax.text(3, 0.28, "보행자에 가로 2점이 걸리는 간격", fontsize=9.5, color=GRAY)
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 1.5)
    ax.set_xlabel("거리 [m]")
    ax.set_ylabel("이웃 점 간격 [m]")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.88))
    ax.set_title("거리별 이웃 점 간격 ≈ R·Δφ", loc="left", fontsize=11)
    out(fig, "point-spacing")


def walk_error() -> None:
    t = np.linspace(-2, 10, 1000)   # ns
    t0, sigma = 3.0, 1.0

    def pulse(a: float) -> np.ndarray:
        return a * np.exp(-0.5 * ((t - t0) / sigma) ** 2)

    thr = 0.2
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    for a, c, lab in ((1.0, COLORS[0], "강한 반사"), (0.3, COLORS[1], "약한 반사")):
        y = pulse(a)
        ax.plot(t, y, color=c, lw=2, label=lab)
        tc = t[np.argmax(y > thr)]
        ax.plot(tc, thr, "o", color=c)
        ax.axvline(tc, color=c, lw=0.8, ls=":")
    ax.axhline(thr, color=GRAY, ls="--", lw=1)
    ax.text(7.2, thr + 0.03, "고정 문턱값", fontsize=9.5, color=GRAY)
    ax.axvline(t0, color=GRAY, lw=0.8)
    ax.text(t0 + 0.1, 1.02, "실제 도착 시각(펄스 중심)", fontsize=9, color=GRAY)
    ax.set_xlim(-1, 9)
    ax.set_ylim(0, 1.12)
    ax.set_xlabel("시간 [ns]  (1 ns = 거리 15 cm)")
    ax.set_ylabel("수신 신호 (정규화)")
    ax.legend(loc="upper right")
    ax.set_title("walk error: 같은 거리라도 약한 반사는 문턱을 늦게 넘는다", loc="left", fontsize=11)
    out(fig, "walk-error")


if __name__ == "__main__":
    setup()
    scan_patterns()
    point_spacing()
    walk_error()
