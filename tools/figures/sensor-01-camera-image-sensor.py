"""sensor-01-camera-image-sensor 그림: 셔터 타이밍, LED 플리커, 렌즈 왜곡 격자."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SLUG = "sensor-01-camera-image-sensor"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def shutter_timing() -> None:
    """행별 노출 구간: 롤링 셔터는 한 줄 시간씩 밀리고, 글로벌 셔터는 동시에 노출한다."""
    rows = 8
    t_exp = 4.0      # ms
    t_line = 1.0     # ms (그림용으로 과장)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for ax, mode in zip(axes, ("rolling", "global")):
        for r in range(rows):
            start = r * t_line if mode == "rolling" else 0.0
            ax.barh(r, t_exp, left=start, height=0.6, color=COLORS[0], alpha=0.85)
            if mode == "rolling":
                read = start + t_exp
            else:
                read = t_exp + r * t_line   # 저장 노드에서 행 단위로 읽음
            ax.plot([read, read + 0.6], [r, r], color=COLORS[1], lw=4, solid_capstyle="butt")
        ax.invert_yaxis()
        ax.set_xlabel("시간 [ms] (그림용 과장)")
        ax.set_xlim(-0.5, 13)
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(range(rows), [f"{r + 1}행" for r in range(rows)])
    axes[0].set_title("롤링 셔터: 행마다 노출 시작이 한 줄 시간씩 밀림", loc="left", fontsize=11)
    axes[1].set_title("글로벌 셔터: 모든 행이 동시에 노출", loc="left", fontsize=11)
    axes[0].annotate("", xy=(rows - 1, rows - 0.3), xytext=(0, rows - 0.3),
                     arrowprops=dict(arrowstyle="<->", color=GRAY))
    axes[0].text((rows - 1) / 2, rows + 0.45, "(행 수 − 1) × 한 줄 시간", ha="center", fontsize=9, color=GRAY)
    axes[0].set_ylim(rows + 0.9, -0.8)
    h1 = plt.Rectangle((0, 0), 1, 1, color=COLORS[0], alpha=0.85)
    h2 = plt.Rectangle((0, 0), 1, 1, color=COLORS[1])
    axes[1].legend([h1, h2], ["노출", "읽기"], loc="upper right", fontsize=9)
    fig.tight_layout()
    out(fig, "shutter-timing")


def led_flicker() -> None:
    """PWM으로 구동되는 LED와 짧은/긴 노출 창의 겹침."""
    f_pwm, duty = 90.0, 0.25      # Hz, 듀티비 (예시값)
    fps = 30.0
    t = np.linspace(0, 100, 20001)  # ms
    led = ((t * 1e-3 * f_pwm) % 1.0) < duty
    period = 1000.0 / f_pwm
    on_starts = np.arange(0, 100, period)
    fig, axes = plt.subplots(2, 1, figsize=(9, 3.9), sharex=True)
    for ax, t_exp, label in zip(axes, (0.5, 12.0), ("짧은 노출 0.5 ms (밝은 낮)", "긴 노출 12 ms (LFM이 노리는 방향)")):
        for t_on in on_starts:
            ax.add_patch(plt.Rectangle((t_on, 0), period * duty, 1, color=COLORS[4], alpha=0.55, lw=0))
        for k in range(3):
            t0 = 5 + k * 1000 / fps
            seen = led[(t >= t0) & (t <= t0 + t_exp)].any()
            ax.axvspan(t0, t0 + max(t_exp, 0.8), ymin=0, ymax=1, color=COLORS[0], alpha=0.35)
            ax.text(t0 + max(t_exp, 0.8) / 2, 1.12, "켜짐으로 찍힘" if seen else "꺼짐으로 찍힘",
                    ha="center", fontsize=9, color=COLORS[2] if seen else COLORS[1])
        ax.set_ylim(0, 1.35)
        ax.set_yticks([0, 1], ["꺼짐", "켜짐"])
        ax.grid(False)
        ax.set_title(label, loc="left", fontsize=10.5)
    axes[1].set_xlabel("시간 [ms]  (LED: 90 Hz PWM·듀티 25% 예시, 파란 띠: 30 fps 프레임의 노출 구간)")
    fig.tight_layout()
    out(fig, "led-flicker")


def distortion_grid() -> None:
    """정규화 좌표에서 방사 왜곡 r_d = r(1 + k1 r^2)를 격자에 적용."""
    fig, axes = plt.subplots(1, 3, figsize=(9, 3.3))
    lines = np.linspace(-1, 1, 9)
    s = np.linspace(-1, 1, 200)
    for ax, k1, title in zip(axes, (0.0, -0.25, 0.25), ("왜곡 없음", "배럴 왜곡 (k₁ < 0)", "핀쿠션 왜곡 (k₁ > 0)")):
        for c in lines:
            for x, y in ((np.full_like(s, c), s), (s, np.full_like(s, c))):
                r2 = x**2 + y**2
                f = 1 + k1 * r2 / 2   # 모서리 r²=2를 1로 정규화
                ax.plot(x * f, y * f, color=COLORS[0], lw=1)
        ax.set_aspect("equal")
        ax.set_xlim(-1.35, 1.35)
        ax.set_ylim(-1.35, 1.35)
        ax.axis("off")
        ax.set_title(title, fontsize=11)
    fig.tight_layout()
    out(fig, "distortion-grid")


if __name__ == "__main__":
    setup()
    shutter_timing()
    led_flicker()
    distortion_grid()
