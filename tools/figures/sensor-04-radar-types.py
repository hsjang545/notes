"""sensor-04-radar-types 그림: CA-CFAR, RCS와 탐지 거리, 다중 경로 고스트."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SLUG = "sensor-04-radar-types"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def ca_cfar(power: np.ndarray, n_train: int, n_guard: int, scale: float) -> np.ndarray:
    """1차원 CA-CFAR 문턱값. 가장자리는 한쪽 학습 셀만 쓴다."""
    n = power.size
    thr = np.full(n, np.nan)
    for i in range(n):
        lo = power[max(0, i - n_guard - n_train): max(0, i - n_guard)]
        hi = power[i + n_guard + 1: i + n_guard + 1 + n_train]
        cells = np.concatenate([lo, hi])
        if cells.size:
            thr[i] = scale * cells.mean()
    return thr


def cfar_figure() -> None:
    rng = np.random.default_rng(3)
    n = 200
    noise = rng.exponential(1.0, n)
    noise[120:] *= 6.0                       # 클러터가 큰 구간
    sig = noise.copy()
    targets = {40: 60.0, 80: 400.0, 84: 25.0, 150: 80.0}   # 셀: 전력(선형). 80 옆 84는 작은 물체
    for k, p in targets.items():
        sig[k] += p
        for d, a in ((1, 0.3), (-1, 0.3)):
            sig[k + d] += p * a
    thr = ca_cfar(sig, n_train=12, n_guard=2, scale=6.0)
    def db(x: np.ndarray) -> np.ndarray:
        return 10 * np.log10(x)

    fig, ax = plt.subplots(figsize=(8.5, 4))
    ax.plot(db(sig), color=COLORS[0], lw=1.2, label="거리 프로파일(검사 셀 전력)")
    ax.plot(db(thr), color=COLORS[1], lw=2, label="CA-CFAR 문턱값")
    det = sig > thr
    ax.plot(np.where(det)[0], db(sig[det]), "o", color=COLORS[2], ms=6, label="검출")
    ax.annotate("작은 물체(놓침):\n옆의 큰 물체가 학습 셀에 들어가\n문턱이 올라감", (84, db(sig[84])), (92, 33),
                fontsize=9, arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.annotate("클러터 증가 구간:\n문턱이 따라 올라감", (130, db(thr[130])), (148, 27), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    ax.set_xlabel("거리 셀 번호")
    ax.set_ylabel("전력 [dB]")
    ax.set_ylim(-15, 46)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3, fontsize=9)
    ax.set_title("CA-CFAR: 주변 학습 셀 평균 × 배수를 문턱으로 쓴다 (모의 데이터)", loc="left", fontsize=11)
    out(fig, "cfar")


def range_vs_rcs() -> None:
    rcs_db = np.linspace(-15, 30, 200)
    r_ref, rcs_ref = 200.0, 10.0   # 10 dBsm 기준 200 m인 가상의 레이더
    r = r_ref * (10 ** ((rcs_db - rcs_ref) / 10)) ** 0.25
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.plot(rcs_db, r, color=COLORS[0], lw=2.2)
    marks = [(-8, "보행자(대략)"), (10, "승용차(대략)\n기준점"), (25, "트럭(대략)")]
    for x, lab in marks:
        y = r_ref * (10 ** ((x - rcs_ref) / 10)) ** 0.25
        ax.plot(x, y, "o", color=COLORS[1])
        ax.annotate(f"{lab}\n{y:.0f} m", (x, y), (x + 1.2, y - 45), fontsize=9)
    ax.set_xlabel("RCS [dBsm]")
    ax.set_ylabel("최대 탐지 거리 [m]")
    ax.set_ylim(0, 520)
    ax.set_title("최대 탐지 거리 ∝ σ^(1/4): 10 dBsm에서 200 m인 레이더의 예", loc="left", fontsize=11)
    ax.text(-14, 480, "RCS 12 dB 감소(1/16) → 거리 절반", fontsize=9.5, color=GRAY)
    out(fig, "range-vs-rcs")


def multipath_ghost() -> None:
    fig, ax = plt.subplots(figsize=(8.5, 4))
    wall_y = 4.0
    radar = np.array([0.0, 0.0])
    target = np.array([40.0, 1.5])
    ghost = np.array([target[0], 2 * wall_y - target[1]])
    # 반사점: 레이더와 고스트를 잇는 직선이 벽과 만나는 점
    s = wall_y / ghost[1]
    refl = radar + s * (ghost - radar)
    ax.axhline(wall_y, color=GRAY, lw=4, alpha=0.6)
    ax.text(1, wall_y + 0.25, "가드레일·방음벽(금속 면)", fontsize=9.5, color=GRAY)
    ax.add_patch(plt.Rectangle((-4.5, -0.9), 4.5, 1.8, color=COLORS[0], alpha=0.8))
    ax.text(-2.25, -2.2, "자차(레이더)", ha="center", fontsize=9.5)
    ax.add_patch(plt.Rectangle((target[0], target[1] - 0.9), 4.5, 1.8, color=COLORS[1], alpha=0.85))
    ax.text(target[0] + 2.25, target[1] - 1.7, "실제 차량", ha="center", fontsize=9.5)
    ax.add_patch(plt.Rectangle((ghost[0], ghost[1] - 0.9), 4.5, 1.8, fill=False, ec=COLORS[1], ls="--", lw=1.5))
    ax.text(ghost[0] + 2.25, ghost[1] + 1.1, "고스트(벽 너머 대칭 위치)", ha="center", fontsize=9.5, color=COLORS[1])
    ax.annotate("", target, radar, arrowprops=dict(arrowstyle="->", color=COLORS[2], lw=1.5))
    ax.plot([radar[0], refl[0], target[0]], [radar[1], refl[1], target[1]], color=COLORS[3], lw=1.5)
    ax.plot([refl[0], ghost[0]], [refl[1], ghost[1]], color=COLORS[3], lw=1, ls=":")
    ax.text(15, -0.9, "직접 경로", color=COLORS[2], fontsize=9.5)
    ax.text(14, 2.9, "벽 반사 경로", color=COLORS[3], fontsize=9.5)
    ax.set_xlim(-6, 50)
    ax.set_ylim(-3, 9)
    ax.set_xlabel("종방향 [m]")
    ax.set_ylabel("횡방향 [m]")
    ax.set_title("다중 경로 고스트: 레이더는 마지막 도착 방향과 경로 길이로 위치를 정한다", loc="left", fontsize=11)
    out(fig, "multipath-ghost")


if __name__ == "__main__":
    setup()
    cfar_figure()
    range_vs_rcs()
    multipath_ghost()
