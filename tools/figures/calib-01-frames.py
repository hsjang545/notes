"""calib-01 좌표계 그림.

1. frames-axes: 차량(base_link, REP-103) 좌표축과 카메라 장착 프레임·광학 프레임 좌표축
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-01-frames"
setup()

AX_COL = {"x": "#D55E00", "y": "#009E73", "z": "#0072B2"}


def _save(fig: plt.Figure, name: str) -> None:
    prev = os.environ.get("FIGCHECK_DIR")
    if prev:
        fig.savefig(os.path.join(prev, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def _frame(ax, origin, R, label, length=1.0, names=("x", "y", "z"), sub=None, label_dz=-0.35) -> None:
    for k, n in enumerate(names):
        d = R[:, k] * length
        ax.quiver(*origin, *d, color=AX_COL[n], lw=2.2, arrow_length_ratio=0.18)
        tip = origin + d * 1.15
        txt = n if sub is None else f"{n}{sub}"
        ax.text(*tip, txt, color=AX_COL[n], fontsize=11, ha="center", va="center", fontweight="bold")
    ax.text(*(origin + np.array([0, 0, label_dz])), label, fontsize=10, ha="center", va="top", color="k")


def frames_axes() -> None:
    fig = plt.figure(figsize=(11.0, 4.8))
    R_cam_opt = np.array([[0, 0, 1], [-1, 0, 0], [0, -1, 0]], float)

    # 왼쪽: base_link와 카메라 장착 프레임(평행)
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    _frame(ax, np.zeros(3), np.eye(3), "base_link\n(x 전방, y 왼쪽, z 위)", 1.0)
    cam = np.array([1.8, 0.0, 1.3])
    _frame(ax, cam, np.eye(3), "", 0.7)
    ax.text(*(cam + np.array([0, -1.0, 0.1])), "cam_front\n(장착 프레임)", fontsize=10, ha="left")
    ax.plot([0, cam[0]], [0, cam[1]], [0, cam[2]], ls="--", color=GRAY, lw=1)
    ax.text(0.7, 0.0, 0.35, "T_base_cam", color=GRAY, fontsize=9)
    ax.set_title("REP-103 몸체 좌표: 차량과 카메라 장착 프레임")

    # 오른쪽: 같은 원점의 장착 프레임과 광학 프레임을 옆으로 떼어 그린다
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")
    oa, ob = np.array([0.0, 1.0, 0.0]), np.array([0.0, -1.0, 0.0])
    _frame(ax2, oa, np.eye(3), "cam_front\n(장착, x 전방)", 0.8)
    _frame(ax2, ob, R_cam_opt, "cam_front_optical\n(광학, z 전방)", 0.8, sub="'", label_dz=-1.05)
    # 광학 프레임 앞의 영상 평면
    f, w, h = 1.6, 0.45, 0.32
    c = ob + np.array([f, 0, 0])
    corners = c + np.array([[0, w, h], [0, -w, h], [0, -w, -h], [0, w, -h], [0, w, h]])
    ax2.plot(corners[:, 0], corners[:, 1], corners[:, 2], color="k", lw=1.2)
    tl = c + np.array([0, w, h])
    ax2.quiver(*tl, 0, -0.4, 0, color="k", lw=1, arrow_length_ratio=0.25)
    ax2.quiver(*tl, 0, 0, -0.3, color="k", lw=1, arrow_length_ratio=0.25)
    ax2.text(*(tl + np.array([0, -0.45, 0.1])), "u", fontsize=10)
    ax2.text(*(tl + np.array([0, 0.12, -0.35])), "v", fontsize=10)
    ax2.text(*(c + np.array([0, -w - 0.05, -h - 0.1])), "영상 평면", fontsize=9, ha="left")
    ax2.set_title("장착 프레임과 광학 프레임 (원점은 같고 축만 다름)")
    ax2.text2D(0.03, 0.0, "x' = -y (오른쪽),  y' = -z (아래),  z' = +x (전방)",
               transform=ax2.transAxes, fontsize=10)

    for a, xl, yl, zl in ((ax, (-0.3, 2.4), (-1.2, 1.2), (-0.8, 1.9)),
                          (ax2, (-0.6, 2.0), (-2.0, 2.0), (-1.5, 1.0))):
        a.set_xlim(*xl)
        a.set_ylim(*yl)
        a.set_zlim(*zl)
        a.set_box_aspect((xl[1] - xl[0], yl[1] - yl[0], zl[1] - zl[0]))
        a.view_init(elev=16, azim=-155)
        a.set_xticks([]); a.set_yticks([]); a.set_zticks([])
        a.xaxis.pane.set_visible(False); a.yaxis.pane.set_visible(False); a.zaxis.pane.set_visible(False)
        a.grid(False)
        a.set_axis_off()
    fig.subplots_adjust(wspace=0.02, left=0, right=1)
    _save(fig, "frames-axes")


if __name__ == "__main__":
    frames_axes()
