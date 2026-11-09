"""calib-02 카메라 모델 그림.

1. pinhole-geometry: 핀홀 투영의 옆모습(Y-Z 평면)
2. distortion-grid: 배럴·핀쿠션·접선 왜곡이 격자를 휘는 모양
3. fisheye-mapping: 투영 함수별 상 높이 r(θ)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-02-camera-model"
setup()


def _save(fig: plt.Figure, name: str) -> None:
    prev = os.environ.get("FIGCHECK_DIR")
    if prev:
        fig.savefig(os.path.join(prev, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def pinhole_geometry() -> None:
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    f, Z, Y = 1.0, 4.2, 1.6
    y = f * Y / Z
    ax.axhline(0, color=GRAY, lw=1, ls="--")
    ax.text(4.75, 0.08, "광축 (z)", color=GRAY, fontsize=10)
    ax.plot(0, 0, "ko", ms=7)
    ax.text(-0.08, -0.2, "투영 중심 C", ha="right", fontsize=10)
    # 영상 평면 (앞쪽 가상 평면)
    ax.plot([f, f], [-1.0, 1.0], color="k", lw=3)
    ax.text(f + 0.05, -1.12, "영상 평면 (z = f)", fontsize=10)
    # 점과 광선
    ax.plot([0, Z], [0, Y], color=COLORS[0], lw=1.8)
    ax.plot(Z, Y, "o", color=COLORS[1], ms=8)
    ax.text(Z + 0.08, Y + 0.02, "P = (X, Y, Z)", fontsize=11, color=COLORS[1])
    ax.plot(f, y, "o", color=COLORS[0], ms=7)
    ax.text(f - 0.06, y + 0.2, "y = f·Y/Z", fontsize=11, color=COLORS[0], ha="right")
    # 치수선
    ax.annotate("", xy=(f, -0.55), xytext=(0, -0.55), arrowprops=dict(arrowstyle="<->", color=GRAY))
    ax.text(f / 2, -0.5, "f", ha="center", fontsize=11, color=GRAY)
    ax.annotate("", xy=(Z, -0.8), xytext=(0, -0.8), arrowprops=dict(arrowstyle="<->", color=GRAY))
    ax.text(Z / 2, -0.75, "Z (깊이)", ha="center", fontsize=10, color=GRAY)
    ax.plot([Z, Z], [0, Y], color=GRAY, lw=1, ls=":")
    ax.text(Z + 0.08, Y / 2, "Y", fontsize=11, color=GRAY)
    # 각도
    th = np.arctan2(Y, Z)
    a = np.linspace(0, th, 30)
    ax.plot(0.6 * np.cos(a), 0.6 * np.sin(a), color=COLORS[2], lw=1.5)
    ax.text(0.65, 0.09, "θ", color=COLORS[2], fontsize=12)
    ax.text(-0.8, 1.8, "y = f·tan θ  →  θ가 90°에 가까우면 y → ∞", fontsize=10, color=COLORS[2])
    ax.set_xlim(-0.9, 5.4)
    ax.set_ylim(-1.25, 2.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("핀홀 투영 (옆에서 본 Y-Z 단면, 광학 좌표계)")
    _save(fig, "pinhole-geometry")


def _distort(x, y, k1=0.0, k2=0.0, p1=0.0, p2=0.0):
    r2 = x * x + y * y
    rad = 1 + k1 * r2 + k2 * r2 * r2
    xd = x * rad + 2 * p1 * x * y + p2 * (r2 + 2 * x * x)
    yd = y * rad + p1 * (r2 + 2 * y * y) + 2 * p2 * x * y
    return xd, yd


def distortion_grid() -> None:
    cases = [
        ("배럴 (k₁ < 0)", dict(k1=-0.25)),
        ("핀쿠션 (k₁ > 0)", dict(k1=0.20)),
        ("접선 (p₁, p₂ ≠ 0)", dict(p1=0.04, p2=0.03)),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.9))
    lines = np.linspace(-0.8, 0.8, 9)
    t = np.linspace(-0.8, 0.8, 40)
    for ax, (title, kw) in zip(axes, cases):
        for c in lines:
            for xs, ys in ((np.full_like(t, c), t), (t, np.full_like(t, c))):
                ax.plot(xs, ys, color="#D1D5DB", lw=0.8)
                xd, yd = _distort(xs, ys, **kw)
                ax.plot(xd, yd, color=COLORS[0], lw=1.3)
        ax.set_title(title)
        ax.set_aspect("equal")
        ax.set_xlim(-1.05, 1.05)
        ax.set_ylim(-1.05, 1.05)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for sp in ax.spines.values():
            sp.set_visible(False)
    fig.text(0.5, 0.02, "회색: 왜곡 없는 정규화 격자,  파랑: radtan 모델로 왜곡된 격자 (정규화 좌표, 과장된 계수)",
             ha="center", fontsize=10, color=GRAY)
    fig.subplots_adjust(bottom=0.1, wspace=0.08)
    _save(fig, "distortion-grid")


def fisheye_mapping() -> None:
    th = np.radians(np.linspace(0, 110, 400))
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    persp = np.where(th < np.radians(89), np.tan(np.minimum(th, np.radians(89))), np.nan)
    curves = [
        ("원근(핀홀) f·tanθ", persp),
        ("등거리 f·θ", th),
        ("등입체각 2f·sin(θ/2)", 2 * np.sin(th / 2)),
        ("정사영 f·sinθ", np.sin(th)),
        ("입체 2f·tan(θ/2)", 2 * np.tan(th / 2)),
    ]
    for (lab, r), c in zip(curves, COLORS):
        ax.plot(np.degrees(th), r, color=c, lw=2, label=lab)
    ax.axvline(90, color=GRAY, ls="--", lw=1)
    ax.text(91, 2.65, "θ = 90°\n(화각 180°)", fontsize=9, color=GRAY)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 3.0)
    ax.set_xlabel("광선이 광축과 이루는 각 θ [°]")
    ax.set_ylabel("상 높이 r / f")
    ax.set_title("투영 함수별 상 높이: 핀홀만 90° 앞에서 발산한다")
    ax.legend(loc="upper left")
    _save(fig, "fisheye-mapping")


if __name__ == "__main__":
    pinhole_geometry()
    distortion_grid()
    fisheye_mapping()
