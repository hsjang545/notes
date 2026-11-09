"""sensor-07-imu 그림: Allan 편차 기울기, 관성 항법 위치 오차 증가."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter  # noqa: E402
import numpy as np  # noqa: E402

SLUG = "sensor-07-imu"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
G = 9.80665


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def plain_log_ticks(ax: plt.Axes) -> None:
    """로그 축 눈금을 10^n 대신 일반 숫자로 표기한다(한글 글꼴에 수식 기호가 없어서)."""
    fmt = FuncFormatter(lambda x, _: f"{x:g}")
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_locator(LogLocator(base=10))
        axis.set_major_formatter(fmt)
        axis.set_minor_formatter(NullFormatter())


def allan_deviation() -> None:
    """IEEE 952 부록의 잡음 항별 Allan 분산 식을 더한 예시 곡선(자이로, °/h)."""
    tau = np.logspace(-2, 5, 400)
    q = 0.5            # 양자화 잡음 계수 [°/h·s]
    n = 18.0           # ARW 계수 [°/h·√s]  (= 0.3 °/√h)
    b = 5.0            # 바이어스 불안정성 계수 [°/h]
    k = 0.1            # RRW 계수 [°/h/√s]
    terms = {
        "양자화 (기울기 −1)": 3 * q**2 / tau**2,
        "ARW (기울기 −1/2)": n**2 / tau,
        "바이어스 불안정성 (기울기 0)": np.full_like(tau, (2 * np.log(2) / np.pi) * b**2),
        "RRW (기울기 +1/2)": k**2 * tau / 3,
    }
    total = np.sqrt(sum(terms.values()))
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    for (lab, v), c in zip(terms.items(), COLORS[1:]):
        ax.loglog(tau, np.sqrt(v), color=c, lw=1.2, ls="--", label=lab)
    ax.loglog(tau, total, color=COLORS[0], lw=2.6, label="전체 Allan 편차 σ(τ)")
    ax.plot(1, n, "o", color=COLORS[2])
    ax.annotate("τ = 1 s에서 읽은 값 = N\n(18 °/h = 0.3 °/√h)", (1, n), (2.2, 60), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    i = np.argmin(total)
    ax.plot(tau[i], total[i], "o", color=COLORS[3])
    ax.annotate("최저점 ÷ 0.664 ≈ 바이어스 불안정성", (tau[i], total[i]), (8, 0.9), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.plot(3, k, "o", color=COLORS[4])
    ax.annotate("+1/2 직선 연장의 τ = 3 s 값 = K", (3, k), (0.03, 0.15), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    plain_log_ticks(ax)
    ax.set_xlim(1e-2, 1e5)
    ax.set_ylim(0.05, 3000)
    ax.set_xlabel("평균 시간 τ [s]")
    ax.set_ylabel("Allan 편차 σ(τ) [°/h]")
    ax.legend(loc="upper right", fontsize=8.5)
    ax.set_title("자이로 Allan 편차의 잡음별 기울기 (예시 모델 곡선)", loc="left", fontsize=11)
    out(fig, "allan-deviation")


def ins_error_growth() -> None:
    t = np.logspace(0, np.log10(600), 300)
    fig, ax = plt.subplots(figsize=(7.5, 4.3))
    cases = [
        ("가속도계 바이어스 1 mg: ½·b·t²", 0.5 * 1e-3 * G * t**2, COLORS[0], "-"),
        ("가속도계 바이어스 0.1 mg", 0.5 * 1e-4 * G * t**2, COLORS[0], "--"),
        ("자이로 바이어스 10 °/h: ⅙·g·b·t³", G * np.radians(10 / 3600) * t**3 / 6, COLORS[1], "-"),
        ("자이로 바이어스 1 °/h", G * np.radians(1 / 3600) * t**3 / 6, COLORS[1], "--"),
    ]
    for lab, e, c, ls in cases:
        ax.loglog(t, e, color=c, ls=ls, lw=2, label=lab)
    ax.axhline(1.0, color=GRAY, lw=0.8)
    ax.text(1.1, 1.25, "1 m", color=GRAY, fontsize=9)
    ax.axhline(0.1, color=GRAY, lw=0.8, ls=":")
    ax.text(1.1, 0.125, "0.1 m", color=GRAY, fontsize=9)
    plain_log_ticks(ax)
    ax.set_xlim(1, 600)
    ax.set_ylim(1e-4, 1e4)
    ax.set_xlabel("보조 센서 없이 지난 시간 [s]")
    ax.set_ylabel("위치 오차 [m]")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("관성 항법 단독 위치 오차의 증가 (단순화한 수평 1축, 슐러 진동 무시)", loc="left", fontsize=10.5)
    out(fig, "ins-error-growth")


if __name__ == "__main__":
    setup()
    allan_deviation()
    ins_error_growth()
