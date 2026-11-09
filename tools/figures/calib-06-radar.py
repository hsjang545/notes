"""calib-06 레이더 단독 캘리브레이션 그림 (합성 데이터).

1. lateral-error: 방위 정렬 오차가 거리에 따라 만드는 횡오차와 차로 폭
2. doppler-fit: 정지물 시선속도-방위 분포와 정렬 오차 곡선 맞춤(RANSAC)
3. azimuth-spread: 정지물 방위 분포 폭에 따른 추정 흩어짐
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-06-radar"
setup()


def _save(fig: plt.Figure, name: str) -> None:
    prev = os.environ.get("FIGCHECK_DIR")
    if prev:
        fig.savefig(os.path.join(prev, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def solve_ls(theta, v_r, v_ego):
    A = np.c_[-v_ego * np.cos(theta), v_ego * np.sin(theta)]
    (a, b), *_ = np.linalg.lstsq(A, v_r, rcond=None)
    return np.arctan2(b, a), np.hypot(a, b)


def solve_ransac(theta, v_r, v_ego, thresh=0.15, iters=300, seed=0):
    """본문 solve_azimuth_ransac과 같은 방식."""
    rng = np.random.default_rng(seed)
    best = np.zeros(len(theta), bool)
    for _ in range(iters):
        idx = rng.choice(len(theta), 2, replace=False)
        d, s = solve_ls(theta[idx], v_r[idx], v_ego[idx])
        inl = np.abs(v_r + s * v_ego * np.cos(theta + d)) < thresh
        if inl.sum() > best.sum():
            best = inl
    d, s = solve_ls(theta[best], v_r[best], v_ego[best])
    return d, s, best


def lateral_error() -> None:
    r = np.linspace(0, 200, 400)
    fig, ax = plt.subplots(figsize=(8.0, 4.3))
    ax.axhspan(1.75, 3.5, color=COLORS[4], alpha=0.12, lw=0)
    ax.axhline(3.5, color=COLORS[4], lw=1, ls="--")
    ax.axhline(1.75, color=COLORS[4], lw=1, ls=":")
    ax.text(3, 3.6, "차로 폭 약 3.5 m (한 차로 옆으로 이동)", color="#9A6700", fontsize=9.5)
    ax.text(3, 1.85, "차로 폭의 절반 (차로 경계를 넘을 수 있음)", color="#9A6700", fontsize=9.5)
    for deg, c in zip([0.25, 0.5, 1.0, 2.0], COLORS):
        ax.plot(r, r * np.sin(np.radians(deg)), color=c, lw=2, label=f"방위 오차 {deg:g}°")
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 7.2)
    ax.set_xlabel("표적 거리 r [m]")
    ax.set_ylabel("횡오차 r·sinΔθ [m]")
    ax.set_title("방위 정렬 오차가 만드는 횡오차")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.88))
    _save(fig, "lateral-error")


def doppler_fit() -> None:
    rng = np.random.default_rng(3)
    true_d = np.radians(1.2)
    n_s, n_m = 800, 200
    theta = rng.uniform(np.radians(-60), np.radians(60), n_s + n_m)
    v_ego = rng.uniform(8.0, 20.0, n_s + n_m)
    v_r = -v_ego * np.cos(theta + true_d) + rng.normal(0, 0.05, n_s + n_m)
    v_r[n_s:] += rng.uniform(-15, 15, n_m)
    d, s, inl = solve_ransac(theta, v_r, v_ego)
    y = v_r / v_ego  # 차량 속도로 정규화
    th = np.linspace(-60, 60, 300)
    thr = np.radians(th)
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(8.6, 6.4), sharex=True, gridspec_kw={"height_ratios": [1.3, 1]})
    ax.scatter(np.degrees(theta[~inl]), y[~inl], s=8, color=GRAY, alpha=0.5, lw=0, label="이상치(움직이는 물체)")
    ax.scatter(np.degrees(theta[inl]), y[inl], s=6, color=COLORS[0], alpha=0.6, lw=0, label="인라이어(정지물)")
    ax.plot(th, -s * np.cos(thr + d), color=COLORS[1], lw=2, label="맞춘 곡선 -s·cos(θ+δ)")
    ax.set_ylim(-1.3, 0.25)
    ax.set_ylabel("시선속도 / 차량 속도")
    ax.set_title(f"정지물 도플러로 방위 정렬 오차 추정 (합성, 참값 δ = +1.20°, 추정 {np.degrees(d):+.2f}°)")
    ax.legend(loc="upper center", fontsize=9, ncol=3)
    # 아래: 정렬 오차가 없을 때의 곡선 -cos θ를 뺀 나머지 ≈ δ·sin θ
    ax2.scatter(np.degrees(theta[inl]), y[inl] + np.cos(theta[inl]), s=6, color=COLORS[0], alpha=0.5, lw=0)
    ax2.plot(th, -s * np.cos(thr + d) + np.cos(thr), color=COLORS[1], lw=2, label="맞춘 곡선 - (-cos θ)")
    ax2.axhline(0, color=GRAY, lw=1.2, ls="--", label="정렬 오차 0")
    ax2.set_ylim(-0.045, 0.045)
    ax2.set_xlim(-62, 62)
    ax2.set_xlabel("레이더 기준 방위 θ [°]")
    ax2.set_ylabel("-cos θ와의 차이")
    ax2.text(-58, 0.03, "차이 ≈ δ·sin θ: 기울기가 정렬 오차다", fontsize=10)
    ax2.legend(loc="lower right", fontsize=9)
    fig.subplots_adjust(hspace=0.12)
    _save(fig, "doppler-fit")


def azimuth_spread() -> None:
    rng = np.random.default_rng(5)
    true_d = np.radians(1.0)
    spreads = [5, 10, 15, 20, 30, 45, 60]
    fig, ax = plt.subplots(figsize=(8.0, 4.0))
    for sig, c, lab in ((0.05, COLORS[0], "시선속도 잡음 0.05 m/s"), (0.15, COLORS[1], "시선속도 잡음 0.15 m/s")):
        stds = []
        for w in spreads:
            est = []
            for _ in range(200):
                th = rng.uniform(np.radians(-w), np.radians(w), 150)
                v = rng.uniform(8, 20, 150)
                vr = -v * np.cos(th + true_d) + rng.normal(0, sig, 150)
                est.append(solve_ls(th, vr, v)[0])
            stds.append(np.degrees(np.std(est)))
        ax.plot(spreads, stds, "o-", color=c, lw=2, label=lab)
    ax.set_yscale("log")
    ax.set_xlabel("정지물 방위 분포 폭 ±w [°]")
    ax.set_ylabel("δ 추정의 표준편차 [°]")
    ax.set_title("검출 150개 구간 하나의 추정 흩어짐: 방위가 넓게 퍼질수록 정확하다")
    ax.set_yticks([0.01, 0.03, 0.1, 0.3, 1])
    ax.set_yticklabels(["0.01", "0.03", "0.1", "0.3", "1"])
    ax.legend()
    _save(fig, "azimuth-spread")


if __name__ == "__main__":
    lateral_error()
    doppler_fit()
    azimuth_spread()
