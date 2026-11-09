"""calib-05 라이다 단독 캘리브레이션 그림 (합성 데이터).

1. ring-residual: 채널 하나의 고도각 오차가 링별 지면 잔차에 나타나는 모양
2. ground-fit: RANSAC 지면 평면으로 roll·pitch·높이 추정(옆에서 본 모습)
3. icp-perturbation: 초기값 섭동 시험, 구조가 풍부한 장면과 복도 장면 비교 (open3d 필요)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from _style import COLORS, GRAY, save, setup  # noqa: E402

SLUG = "calib-05-lidar"
setup()


def _save(fig: plt.Figure, name: str) -> None:
    prev = os.environ.get("FIGCHECK_DIR")
    if prev:
        fig.savefig(os.path.join(prev, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def rot_x(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def make_T(xyz, rpy_deg) -> np.ndarray:
    r, p, y = np.radians(rpy_deg)
    T = np.eye(4)
    T[:3, :3] = rot_z(y) @ rot_y(p) @ rot_x(r)
    T[:3, 3] = xyz
    return T


def fit_plane(points: np.ndarray, dist: float = 0.03, iters: int = 300, seed: int = 0):
    """본문 fit_plane_ransac과 같은 방식(RANSAC + SVD 재추정)."""
    rng = np.random.default_rng(seed)
    best = np.zeros(len(points), bool)
    for _ in range(iters):
        p0, p1, p2 = points[rng.choice(len(points), 3, replace=False)]
        n = np.cross(p1 - p0, p2 - p0)
        if np.linalg.norm(n) < 1e-9:
            continue
        n /= np.linalg.norm(n)
        inl = np.abs(points @ n - n @ p0) < dist
        if inl.sum() > best.sum():
            best = inl
    q = points[best]
    c = q.mean(axis=0)
    n = np.linalg.svd(q - c, full_matrices=False)[2][-1]
    n = -n if n[2] < 0 else n
    return n, float(-n @ c), best


def ring_residual() -> None:
    rng = np.random.default_rng(0)
    h, bad, err = 1.85, 20, np.deg2rad(0.3)
    el = np.deg2rad(np.linspace(-25, 5, 32))
    R_bl = rot_y(np.deg2rad(-2.0)) @ rot_x(np.deg2rad(1.5))
    pts, rings = [], []
    az = np.linspace(-np.pi, np.pi, 900, endpoint=False)
    for k, e in enumerate(el):
        e_true = e + (err if k == bad else 0.0)
        d_true = np.c_[np.cos(e_true) * np.cos(az), np.cos(e_true) * np.sin(az),
                       np.full(az.shape, np.sin(e_true))]
        db = d_true @ R_bl.T
        with np.errstate(divide="ignore"):
            t = -h / db[:, 2]
        ok = (t > 2.0) & (t < 40.0)
        r = t[ok] + rng.normal(0, 0.02, ok.sum())
        d_nom = np.c_[np.cos(e) * np.cos(az[ok]), np.cos(e) * np.sin(az[ok]), np.full(ok.sum(), np.sin(e))]
        pts.append(d_nom * r[:, None])
        rings.append(np.full(ok.sum(), k))
    pts, rings = np.vstack(pts), np.concatenate(rings)
    n, d, _ = fit_plane(pts)
    near = np.abs(pts @ n + d) < 0.3  # 본문 ring_residuals의 band
    resid = pts @ n + d
    ks, med, mad = [], [], []
    for k in np.unique(rings[near]):
        r = resid[near & (rings == k)]
        if len(r) < 50:
            continue
        ks.append(k)
        med.append(np.median(r))
        mad.append(np.median(np.abs(r - np.median(r))))
    ks, med, mad = np.array(ks), np.array(med) * 100, np.array(mad) * 100
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    cols = [COLORS[1] if k == bad else COLORS[0] for k in ks]
    ax.bar(ks, med, color=cols, yerr=mad, ecolor=GRAY, capsize=2)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("채널(링) 번호 (작을수록 아래를 보는 빔, 지면을 가까이에서 맞힘)")
    ax.set_ylabel("지면 평면 잔차 중앙값 [cm]")
    ax.set_title("링별 지면 잔차: 채널 20의 고도각만 0.3° 틀린 경우 (합성, 오차 막대 ±MAD)")
    i = int(np.where(ks == bad)[0][0])
    ax.annotate("고도각 오차 채널", xy=(bad, med[i]), xytext=(bad - 9, med[i] * 0.85), fontsize=10,
                arrowprops=dict(arrowstyle="->", color=GRAY))
    _save(fig, "ring-residual")


def ground_fit() -> None:
    rng = np.random.default_rng(1)
    roll, pitch, h = np.deg2rad(1.5), np.deg2rad(-2.0), 1.85
    ground = np.c_[rng.uniform(2, 30, 5000), rng.uniform(-10, 10, 5000), rng.normal(0, 0.01, 5000)]
    clutter = np.c_[rng.uniform(2, 30, 1500), rng.uniform(-10, 10, 1500), rng.uniform(0.2, 2.5, 1500)]
    P = np.vstack([ground, clutter])
    R_bl = rot_y(pitch) @ rot_x(roll)
    pl = (P - np.array([1.2, 0, h])) @ R_bl
    n, d, inl = fit_plane(pl)
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    sub = np.random.default_rng(9).random(len(pl)) < 0.3  # 그림을 가볍게 하려고 일부만 그린다
    ax.plot(pl[~inl & sub, 0], pl[~inl & sub, 2], ".", ms=2, color=GRAY, alpha=0.5, label="이상치(지면 위 물체)", rasterized=True)
    ax.plot(pl[inl & sub, 0], pl[inl & sub, 2], ".", ms=2, color=COLORS[0], alpha=0.6, label="RANSAC 인라이어(지면)", rasterized=True)
    xs = np.linspace(0, 30, 2)
    zs = -(n[0] * xs + d) / n[2]  # y = 0 단면
    ax.plot(xs, zs, color=COLORS[1], lw=2, label="맞춘 평면 (y = 0 단면)")
    ax.plot(0, 0, "k^", ms=9)
    ax.text(0.4, 0.15, "라이다 원점", fontsize=10)
    ax.annotate("", xy=(0, -d / n[2]), xytext=(0, 0), arrowprops=dict(arrowstyle="<->", color=COLORS[2]))
    ax.text(0.4, -1.0, f"높이 d = {d:.3f} m", color=COLORS[2], fontsize=10)
    est_p = np.degrees(np.arctan2(-n[0], np.hypot(n[1], n[2])))
    est_r = np.degrees(np.arctan2(n[1], n[2]))
    ax.text(14, 1.0, f"추정 pitch {est_p:+.2f}° (참 -2.00°)\n추정 roll  {est_r:+.2f}° (참 +1.50°)",
            fontsize=10, bbox=dict(facecolor="white", edgecolor=GRAY))
    ax.set_xlim(-1, 30)
    ax.set_ylim(-3.2, 1.9)
    ax.set_xlabel("라이다 x [m] (전방)")
    ax.set_ylabel("라이다 z [m]")
    ax.set_title("지면 평면 맞춤 (옆에서 본 라이다 좌표, 합성 데이터)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3, markerscale=4, fontsize=9)
    _save(fig, "ground-fit")


def _scene(rng, corridor: bool, n: int = 40000) -> np.ndarray:
    # 복도는 센서 거리 한계(40 m)보다 길게 만들어 벽 끝이 보이지 않게 한다
    yw, xl = (6.0, 70.0) if corridor else (20.0, 25.0)
    n = n * 2 if corridor else n
    pts = [np.c_[rng.uniform(-xl, xl, n), rng.uniform(-yw, yw, n), np.zeros(n)]]
    m = n // 3
    pts.append(np.c_[rng.uniform(-xl, xl, m), np.full(m, 6.0 if corridor else 15.0), rng.uniform(0, 4, m)])
    pts.append(np.c_[rng.uniform(-xl, xl, m), np.full(m, -6.0 if corridor else -12.0), rng.uniform(0, 4, m)])
    if not corridor:
        pts.append(np.c_[np.full(m, 22.0), rng.uniform(-12, 15, m), rng.uniform(0, 5, m)])
        for cx, cy in [(8, 5), (12, -6), (-6, 8), (15, 2), (-10, -7)]:
            a = rng.uniform(0, 2 * np.pi, 2000)
            pts.append(np.c_[cx + 0.3 * np.cos(a), cy + 0.3 * np.sin(a), rng.uniform(0, 4, 2000)])
    return np.vstack(pts)


def icp_perturbation() -> None:
    import open3d as o3d

    reg = o3d.pipelines.registration

    def prep(pc, v):
        q = pc.voxel_down_sample(v)
        q.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=v * 3, max_nn=30))
        return q

    def run(src, tgt, init):
        T = init
        for v in (0.5, 0.25, 0.1):
            s, t = prep(src, v), prep(tgt, v)
            T = reg.registration_icp(s, t, v * 2.0, T, reg.TransformationEstimationPointToPlane(),
                                     reg.ICPConvergenceCriteria(1e-6, 1e-6, 50)).transformation
        return T

    T_b_main = make_T([1.2, 0, 1.9], [0.5, -1.0, 0.3])
    T_b_aux = make_T([2.1, -0.7, 0.6], [1.0, 2.0, -35.0])
    T_true = np.linalg.inv(T_b_main) @ T_b_aux
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))
    cases = ((False, COLORS[0], "구조가 풍부한 장면"), (True, COLORS[1], "복도(바닥 + 평행한 두 벽)"))
    for corridor, c, lab in cases:
        rng = np.random.default_rng(3)
        P = _scene(rng, corridor)
        clouds = []
        for T in (T_b_main, T_b_aux):
            p = (P - T[:3, 3]) @ T[:3, :3]
            r = np.linalg.norm(p, axis=1)
            p = p[(r > 1) & (r < 40)]
            p = p + rng.normal(0, 0.02, p.shape)
            clouds.append(o3d.geometry.PointCloud(o3d.utility.Vector3dVector(p)))
        main, aux = clouds
        e0, e1 = [], []
        for _ in range(20):
            init = T_true @ make_T(rng.uniform(-0.2, 0.2, 3), rng.uniform(-2, 2, 3))
            T = run(aux, main, init)
            e0.append(np.linalg.norm(init[:3, 3] - T_true[:3, 3]) * 100)
            e1.append(np.linalg.norm(T[:3, 3] - T_true[:3, 3]) * 100)
        axes[0].scatter(e0, np.maximum(e1, 1e-3), color=c, s=28, label=lab, alpha=0.8)
        # 참값에서 계산한 point-to-plane 정보 행렬의 이동 블록 고유값(본문 degeneracy_check와 같은 식)
        s_, t_ = prep(aux, 0.1), prep(main, 0.1)
        s_.transform(T_true)
        tree = o3d.geometry.KDTreeFlann(t_)
        tn = np.asarray(t_.normals)
        H = np.zeros((3, 3))
        for p in np.asarray(s_.points):
            _, idx, d2 = tree.search_knn_vector_3d(p, 1)
            if d2[0] < 0.04:
                n = tn[idx[0]]
                H += np.outer(n, n)
        w = np.linalg.eigvalsh(H)
        xs = np.arange(3) + (0.2 if corridor else -0.2)
        axes[1].bar(xs, w / w.max(), width=0.38, color=c, label=lab)
    ax = axes[0]
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    ax.set_xlabel("초기값 이동 오차 [cm]")
    ax.set_ylabel("정합 후 이동 오차 [cm]")
    ax.set_title("초기값 20개의 수렴 결과: 둘 다 한 점으로 모인다")
    ax.legend(loc="center right", fontsize=9)
    ax = axes[1]
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["가장 작은 값", "중간 값", "가장 큰 값"])
    ax.set_ylabel("이동 블록 고유값 (최댓값 = 1)")
    ax.set_title("point-to-plane 정보 행렬: 복도는 한 방향이 거의 0")
    ax.legend(loc="upper left", fontsize=9)
    fig.subplots_adjust(wspace=0.28)
    _save(fig, "icp-perturbation")


if __name__ == "__main__":
    ring_residual()
    ground_fit()
    icp_perturbation()
