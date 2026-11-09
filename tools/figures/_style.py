"""기술노트 그림 공통 스타일.

각 그림 스크립트는 `tools/figures/<글 파일명>.py`에 두고 `assets/img/<글 파일명>/`에 SVG를 쓴다.
    from _style import setup, save, COLORS
    setup()
    fig, ax = plt.subplots()
    ...
    save(fig, "sync-00-why", "error-vs-speed")
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

# 색약에서도 구분되는 팔레트(Okabe-Ito 기반). 순서대로 계열 색으로 쓴다.
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000"]
GRAY = "#6B7280"


def _korean_font() -> str:
    """설치된 한글 글꼴 중 첫 번째. 없는 글꼴을 목록에 넣으면 글자마다 경고가 나서 하나만 고른다."""
    from matplotlib import font_manager

    names = {f.name for f in font_manager.fontManager.ttflist}
    for name in ("Malgun Gothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR"):
        if name in names:
            return name
    raise RuntimeError("한글 글꼴이 없다: Malgun Gothic, NanumGothic 등을 설치한다.")


def setup() -> None:
    """한글 글꼴, 흰 배경, 글자를 윤곽선으로 저장(보는 기기에 글꼴이 없어도 같게 보임)."""
    plt.rcParams.update(
        {
            "font.family": [_korean_font(), "DejaVu Sans"],
            "axes.unicode_minus": False,
            "svg.fonttype": "path",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "figure.dpi": 100,
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.grid": True,
            "grid.color": "#E5E7EB",
            "grid.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.prop_cycle": matplotlib.cycler(color=COLORS),
            "legend.frameon": False,
        }
    )


def save(fig: plt.Figure, slug: str, name: str) -> Path:
    """assets/img/<slug>/<name>.svg로 저장하고 경로를 돌려준다."""
    out = ROOT / "assets" / "img" / slug / f"{name}.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg", bbox_inches="tight", pad_inches=0.15, metadata={"Date": None})
    plt.close(fig)
    return out
