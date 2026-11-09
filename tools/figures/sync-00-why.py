"""sync-00-why 그림: 시간 오차가 위치·투영 오차로 바뀌는 크기."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from _style import setup, save, COLORS, GRAY

PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def _save(fig, name):
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"sync-00-why-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, "sync-00-why", name)


def error_vs_speed() -> None:
    v_kmh = np.linspace(0, 200, 201)
    dts_ms = [0.1, 1.0, 10.0, 50.0]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for c, dt in zip(COLORS, dts_ms):
        e_cm = v_kmh / 3.6 * dt / 1000 * 100
        ax.plot(v_kmh, e_cm, color=c, lw=2, label=f"Δt = {dt:g} ms")
    ax.set_yscale("log")
    ax.set_ylim(0.01, 700)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:g}"))
    ax.set_xlim(0, 200)
    ax.axhline(10, color=GRAY, ls="--", lw=1)
    box = dict(facecolor="white", edgecolor="none", pad=1.5)
    ax.text(197, 7.0, "예: 매칭 허용 오차 10 cm", color=GRAY, fontsize=9, ha="right", bbox=box)
    ax.axhline(300, color=GRAY, ls=":", lw=1)
    ax.text(197, 380, "차선 폭 약 3 m", color=GRAY, fontsize=9, ha="right")
    ax.set_xlabel("상대 속도 [km/h]")
    ax.set_ylabel("위치 오차 [cm] (로그)")
    ax.set_title("상대 속도와 시간 오차에 따른 위치 오차  e = v·Δt")
    ax.legend(loc="lower right", ncol=2)
    _save(fig, "error-vs-speed")


def pixel_vs_yaw() -> None:
    w_dps = np.linspace(0.5, 40, 200)
    dts_ms = [1.0, 10.0, 50.0]
    f_px = 1000.0
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for c, dt in zip(COLORS, dts_ms):
        e_px = f_px * np.tan(np.radians(w_dps) * dt / 1000)
        ax.plot(w_dps, e_px, color=c, lw=2, label=f"Δt = {dt:g} ms")
    ax.axhline(1, color=GRAY, ls="--", lw=1)
    ax.text(39.5, 1.15, "1 px", color=GRAY, fontsize=9, ha="right")
    ax.axvspan(15, 40, color="#F3F4F6", zorder=0)
    ax.text(27.5, 0.012, "교차로 저속 회전 영역(대략)", ha="center", color=GRAY, fontsize=9)
    ax.set_xlim(0, 40)
    ax.set_yscale("log")
    ax.set_ylim(0.01, 100)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:g}"))
    ax.set_xlabel("요레이트 [deg/s]")
    ax.set_ylabel("투영 오차 [px] (로그)")
    ax.set_title("회전 중 투영 오차  e ≈ f·tan(ω·Δt),  f = 1000 px")
    ax.legend(loc="upper left", ncol=3)
    _save(fig, "pixel-vs-yaw")


if __name__ == "__main__":
    setup()
    error_vs_speed()
    pixel_vs_yaw()
