"""calib-03 카메라 내부 캘리브레이션 그림 (합성 데이터, opencv-python 필요).

1. coverage: 가운데에 몰린 데이터와 영상 전체를 덮는 데이터의 코너 분포와 추정 결과
2. per-view-error: 뷰별 재투영 오차와 이상 영상 판정 기준
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-03-camera-intrinsic"
setup()

W, H = 1280, 800
K_TRUE = np.array([[900.0, 0, 645], [0, 900.0, 398], [0, 0, 1]])
D_TRUE = np.array([-0.28, 0.09, 0.0008, -0.0005, -0.012])
GRID = np.zeros((54, 3), np.float32)
GRID[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2) * 0.04
CENTER = np.array([0.16, 0.10, 0.0])


def _save(fig: plt.Figure, name: str) -> None:
    prev = os.environ.get("FIGCHECK_DIR")
    if prev:
        fig.savefig(os.path.join(prev, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def _views(rng, n, tilt, spread, zr):
    obj, img = [], []
    while len(obj) < n:
        R = cv2.Rodrigues(np.deg2rad(rng.uniform(-tilt, tilt, 3) * np.array([1, 1, 0.4])))[0]
        z = rng.uniform(*zr)
        c = rng.uniform(-1, 1, 2) * np.array(spread) * z
        t = np.array([c[0], c[1], z]) - R @ CENTER
        p, _ = cv2.projectPoints(GRID, cv2.Rodrigues(R)[0], t, K_TRUE, D_TRUE)
        p = p.reshape(-1, 2)
        if np.all((p > 5) & (p < [W - 5, H - 5])):
            obj.append(GRID)
            img.append((p + rng.normal(0, 0.15, p.shape)).astype(np.float32))
    return obj, img


def coverage() -> None:
    rng = np.random.default_rng(7)
    sets = [
        ("가운데·정면 위주 (나쁜 예)", _views(rng, 20, 6, (0.12, 0.08), (1.0, 1.3))),
        ("가장자리·기울기·거리 다양 (좋은 예)", _views(rng, 20, 35, (0.48, 0.32), (0.6, 1.6))),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.3))
    for ax, (title, (obj, img)), c in zip(axes, sets, COLORS):
        allp = np.vstack(img)
        ax.plot(allp[:, 0], allp[:, 1], ".", ms=2.5, color=c, alpha=0.6, rasterized=True)
        _, K, D, _, _, std, _, _ = cv2.calibrateCameraExtended(obj, img, (W, H), None, None)
        ax.set_xlim(0, W)
        ax.set_ylim(H, 0)
        ax.set_aspect("equal")
        ax.set_title(title)
        ax.set_xticks([0, 640, 1280])
        ax.set_yticks([0, 400, 800])
        txt = (f"fx = {K[0, 0]:.1f} ± {std[0, 0]:.1f} px (참 900)\n"
               f"k1 = {D[0, 0]:+.3f} ± {std[4, 0]:.3f} (참 -0.280)")
        ax.text(0.02, 0.03, txt, transform=ax.transAxes, fontsize=9.5,
                bbox=dict(facecolor="white", edgecolor=GRAY, alpha=0.9))
    fig.text(0.5, 0.0, "합성 데이터 20장씩, 코너 잡음 0.15 px. 점은 모든 영상의 코너 위치, ± 값은 calibrateCameraExtended의 표준편차",
             ha="center", fontsize=9.5, color=GRAY)
    fig.subplots_adjust(bottom=0.12, wspace=0.12)
    _save(fig, "coverage")


def per_view_error() -> None:
    rng = np.random.default_rng(11)
    obj, img = _views(rng, 24, 35, (0.48, 0.32), (0.6, 1.6))
    img[6] = img[6] + rng.normal(0, 0.6, img[6].shape).astype(np.float32)      # 흐린 영상
    img[15][10:14] += np.float32([2.5, -2.0])                                  # 코너 몇 개 오검출
    _, K, D, _, _, _, _, pv = cv2.calibrateCameraExtended(obj, img, (W, H), None, None)
    pv = pv.ravel()
    med = np.median(pv)
    thresh = med + 3 * np.median(np.abs(pv - med))
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    cols = [COLORS[1] if e > thresh else COLORS[0] for e in pv]
    ax.bar(np.arange(len(pv)), pv, color=cols)
    ax.axhline(thresh, color=COLORS[1], ls="--", lw=1.2, label="판정 기준: 중앙값 + 3·MAD")
    ax.axhline(med, color=GRAY, ls=":", lw=1.2, label="중앙값")
    ax.legend(loc="center right")
    ax.annotate("흐린 영상", xy=(6, pv[6]), xytext=(2.0, pv[6] * 0.95), fontsize=10,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.annotate("코너 4개 오검출", xy=(15, pv[15]), xytext=(17.0, pv[15] * 0.95), fontsize=10,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.set_xlabel("영상 번호")
    ax.set_ylabel("뷰별 RMS 재투영 오차 [px]")
    ax.set_title("뷰별 오차: 특정 영상만 튀면 그 영상을 빼고 다시 돌린다 (합성 데이터)")
    ax.set_xticks(np.arange(0, len(pv), 2))
    _save(fig, "per-view-error")


if __name__ == "__main__":
    coverage()
    per_view_error()
