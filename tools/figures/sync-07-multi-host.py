"""sync-07-multi-host 그림: 홀드오버 중 시간 오차 증가(가정값 계산), 기준을 잃었을 때 두 정책 비교."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from _style import setup, save, COLORS, GRAY

SLUG = "sync-07-multi-host"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def _save(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def holdover_error() -> None:
    """x(t) = y0·t + ½·a·t². y0: 기준을 잃는 순간 남은 주파수 오차, a: 주파수 변화율(온도·노화 묶음)."""
    t = np.logspace(0, np.log10(24 * 3600), 400)  # 1 s ~ 1 day
    cases = [
        ("일반 수정 발진기(XO)", 1e-7, 1e-11),
        ("온도 보상(TCXO)", 1e-8, 1e-12),
        ("항온조(OCXO)", 1e-10, 1e-14),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    for c, (name, y0, a) in zip(COLORS, cases):
        x = np.abs(y0 * t + 0.5 * a * t**2)
        ax.plot(t / 60, x * 1e6, color=c, lw=2, label=f"{name}: y₀={y0:.0e}, a={a:.0e}/s")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1 / 60, 24 * 60)
    ax.set_ylim(1e-4, 1e5)
    fmt = FuncFormatter(lambda v, _: f"{v:g}")
    ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(fmt)
    for y, txt in [(1.0, "1 µs"), (1000.0, "1 ms")]:
        ax.axhline(y, color=GRAY, ls="--", lw=1)
        ax.text(1.2 / 60, y * 1.4, txt, color=GRAY, fontsize=9)
    for m, txt in [(10, "10분(터널·지하)"), (60, "1시간")]:
        ax.axvline(m, color=GRAY, ls=":", lw=1)
        ax.text(m * 1.08, 2e-4, txt, color=GRAY, fontsize=9, rotation=90, va="bottom")
    ax.set_xlabel("기준을 잃은 뒤 경과 시간 [분] (로그)")
    ax.set_ylabel("누적 시간 오차 [µs] (로그)")
    ax.set_title("홀드오버 중 시간 오차 증가: 가정값으로 계산한 예")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), fontsize=9, ncol=1)
    _save(fig, "holdover-error")


def failover_policies() -> None:
    """GM이 사라진 뒤 두 호스트의 시간(GM 기준 오차): 단일 GM 고정 vs 각자 마스터가 되는 경우."""
    rng = np.random.default_rng(7)
    t = np.linspace(0, 600, 1201)  # s
    t_fail = 200.0
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8), sharey=True)
    # 왼쪽: slaveOnly, 각자 마지막 주파수로 자유 진행
    for c, (y0, name) in zip(COLORS, [(2e-8, "호스트 1"), (-3e-8, "호스트 2")]):
        e = np.where(t < t_fail, 0.0, y0 * (t - t_fail)) * 1e6 + rng.normal(0, 0.05, t.size)
        axes[0].plot(t, e, color=c, lw=1.5, label=name)
    axes[0].set_title("단일 GM 고정(slaveOnly): 천천히 벌어짐")
    # 오른쪽: 호스트 2가 마스터가 되며 호스트 1을 끌고 감, 그 과정에서 step
    e1 = np.where(t < t_fail, 0.0, 2e-8 * (t - t_fail))
    e2 = np.where(t < t_fail, 0.0, -3e-8 * (t - t_fail))
    t_sw = 260.0
    jump = (e2 - e1)[np.searchsorted(t, t_sw)]
    e1 = np.where(t < t_sw, e1, e2)  # 호스트 1이 새 마스터(호스트 2)를 따라감
    axes[1].plot(t, e1 * 1e6 + rng.normal(0, 0.05, t.size), color=COLORS[0], lw=1.5, label="호스트 1")
    axes[1].plot(t, e2 * 1e6 + rng.normal(0, 0.05, t.size), color=COLORS[1], lw=1.5, label="호스트 2(새 마스터)")
    axes[1].annotate(f"BMCA로 새 마스터 선택\n호스트 1 시계 step ≈ {jump * 1e6:.1f} µs",
                     xy=(t_sw, e2[np.searchsorted(t, t_sw)] * 1e6), xytext=(330, 6),
                     arrowprops=dict(arrowstyle="->", color=GRAY), fontsize=9, color="black")
    axes[1].set_title("다른 호스트가 마스터가 됨: 시간축이 바뀜")
    for ax in axes:
        ax.axvline(t_fail, color=GRAY, ls="--", lw=1)
        ax.text(t_fail + 5, 9, "GM 정지", color=GRAY, fontsize=9)
        ax.set_xlabel("시간 [s]")
        ax.legend(loc="lower left", fontsize=9)
    axes[0].set_ylabel("원래 GM 시간 기준 오차 [µs]")
    axes[0].set_ylim(-13, 11)
    fig.suptitle("GM이 사라졌을 때 두 정책의 동작(합성 데이터 예시)", fontsize=12)
    fig.tight_layout()
    _save(fig, "failover-policies")


if __name__ == "__main__":
    setup()
    holdover_error()
    failover_policies()
