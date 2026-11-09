"""sensor-02-camera-types 그림: 스테레오 깊이 오차, 어안 투영 모델."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SLUG = "sensor-02-camera-types"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def stereo_depth_error() -> None:
    f_px, dd = 1000.0, 0.25
    z = np.linspace(1, 100, 400)
    fig, ax = plt.subplots(figsize=(7.5, 4))
    for b, c in zip((0.12, 0.3, 0.5), COLORS):
        ax.plot(z, z**2 / (f_px * b) * dd, color=c, lw=2, label=f"기준선 B = {b:.2f} m")
    ax.plot([30, 60], [0.75, 3.0], "o", color=COLORS[1], ms=6)
    ax.annotate("30 m에서 0.75 m", (30, 0.75), (12, 4.2), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.annotate("60 m에서 3 m", (60, 3.0), (42, 7.5), fontsize=9.5, arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 12)
    ax.set_xlabel("거리 Z [m]")
    ax.set_ylabel("깊이 오차 δZ [m]")
    ax.set_title("스테레오 깊이 오차 δZ ≈ Z²·δd / (f·B)   (f = 1,000 px, δd = 0.25 px)", loc="left", fontsize=11)
    ax.legend(loc="upper left")
    out(fig, "stereo-depth-error")


def projection_models() -> None:
    th = np.radians(np.linspace(0, 100, 500))
    fig, ax = plt.subplots(figsize=(7.5, 4))
    models = [
        ("핀홀(투시) r = f·tanθ", np.where(th < np.radians(80), np.tan(th), np.nan), COLORS[6]),
        ("등거리(equidistant) r = f·θ", th, COLORS[0]),
        ("등입체각(equisolid) r = 2f·sin(θ/2)", 2 * np.sin(th / 2), COLORS[2]),
        ("입체투영(stereographic) r = 2f·tan(θ/2)", 2 * np.tan(th / 2), COLORS[1]),
    ]
    for label, r, c in models:
        ax.plot(np.degrees(th), r, color=c, lw=2, label=label)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 3)
    ax.axvline(90, color=GRAY, lw=0.8, ls="--")
    ax.text(91, 0.15, "θ = 90°\n(화각 180°)", fontsize=9, color=GRAY)
    ax.set_xlabel("광축과 입사 광선의 각 θ [°]")
    ax.set_ylabel("영상 중심으로부터 거리 r / f")
    ax.set_title("투영 모델별 r(θ): 핀홀은 90°에서 무한대로 발산", loc="left", fontsize=11)
    ax.legend(loc="upper left", fontsize=9.5)
    out(fig, "projection-models")


if __name__ == "__main__":
    setup()
    stereo_depth_error()
    projection_models()
