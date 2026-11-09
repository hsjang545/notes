"""sensor-06-lidar-data 그림: 회전 중 모션 왜곡과 보정, 안개 감쇠."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SLUG = "sensor-06-lidar-data"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


# 본문의 deskew_planar와 같은 코드 (본문 예제가 동작하는지 함께 확인한다)
def rot_z(yaw: np.ndarray) -> np.ndarray:
    c, s = np.cos(yaw), np.sin(yaw)
    r = np.zeros((yaw.size, 3, 3))
    r[:, 0, 0], r[:, 0, 1] = c, -s
    r[:, 1, 0], r[:, 1, 1] = s, c
    r[:, 2, 2] = 1.0
    return r


def deskew_planar(points: np.ndarray, dt: np.ndarray, v: float, yaw_rate: float, t_ref: float) -> np.ndarray:
    if points.shape[0] != dt.shape[0]:
        raise ValueError("points와 dt의 길이가 다르다")
    tau = dt - t_ref
    yaw = yaw_rate * tau
    trans = np.stack([v * tau, 0.5 * v * yaw_rate * tau**2, np.zeros_like(tau)], axis=1)
    return np.einsum("nij,nj->ni", rot_z(yaw), points) + trans


def ray_box(origin: np.ndarray, d: np.ndarray, xmin: float, xmax: float, ymin: float, ymax: float) -> float:
    """상자 내부에서 쏜 광선이 벽에 닿는 거리."""
    ts = []
    for o, di, lo, hi in ((origin[0], d[0], xmin, xmax), (origin[1], d[1], ymin, ymax)):
        if abs(di) > 1e-12:
            ts += [(lo - o) / di, (hi - o) / di]
    return min(t for t in ts if t > 0)


def motion_distortion() -> None:
    v, w = 20.0, np.radians(30.0)        # 20 m/s, 요레이트 30°/s
    f_rot, n = 10.0, 1800
    dt = np.arange(n) / (n * f_rot)      # 0~100 ms
    az = 2 * np.pi * f_rot * dt - np.pi  # 뒤쪽(−180°)에서 시작해 한 바퀴
    box = (-25.0, 35.0, -12.0, 12.0)
    pts = np.zeros((n, 3))
    for i in range(n):
        yaw = w * dt[i]
        pos = np.array([v * np.sin(yaw) / w, v * (1 - np.cos(yaw)) / w])
        d_world = np.array([np.cos(yaw + az[i]), np.sin(yaw + az[i])])
        r = ray_box(pos, d_world, *box)
        pts[i, :2] = r * np.array([np.cos(az[i]), np.sin(az[i])])   # 그 순간의 센서 좌표계
    fixed = deskew_planar(pts, dt, v, w, t_ref=0.0)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True, constrained_layout=True)
    xmin, xmax, ymin, ymax = box
    for ax, p, title in ((axes[0], pts, "보정 전: 점을 그대로 한 좌표계에 둠"),
                         (axes[1], fixed, "보정 후: 프레임 시작 시각 좌표계로 옮김")):
        ax.plot([xmin, xmax, xmax, xmin, xmin], [ymin, ymin, ymax, ymax, ymin], color=GRAY, lw=1, ls="--")
        ax.scatter(p[:, 0], p[:, 1], c=dt * 1e3, s=3, cmap="viridis", rasterized=True)
        ax.plot(0, 0, "^", color=COLORS[1], ms=9)
        ax.set_aspect("equal")
        ax.set_xlim(-30, 40)
        ax.set_ylim(-16, 16)
        ax.set_xlabel("x [m] (전방)")
        ax.set_title(title, loc="left", fontsize=10.5)
    axes[0].set_ylabel("y [m]")
    axes[0].annotate("시작·끝 경계(seam)\n벽이 어긋남", (-25, 1), (-14, -7), fontsize=9,
                     arrowprops=dict(arrowstyle="->", color=GRAY))
    fig.set_dpi(150)
    sm = plt.cm.ScalarMappable(cmap="viridis", norm=plt.Normalize(0, 100))
    cb = fig.colorbar(sm, ax=axes, shrink=0.8, pad=0.01, aspect=25)
    cb.set_label("점의 측정 시각 [ms]")
    fig.suptitle("10 Hz 회전 라이다, 20 m/s 직진 + 요레이트 30°/s (점선: 실제 벽, 프레임 시작 기준)",
                 x=0.01, ha="left", fontsize=11)
    out(fig, "motion-distortion")


def fog_attenuation() -> None:
    r = np.linspace(1, 250, 500)
    fig, ax = plt.subplots(figsize=(7.5, 4))
    cases = [(None, "맑음 (감쇠 무시)"), (1000.0, "가시거리 1 km"), (200.0, "가시거리 200 m"), (50.0, "가시거리 50 m")]
    p_thr = 10 * np.log10(1 / 200.0**2)   # 맑은 날 200 m에서 겨우 검출된다고 가정
    for (vis, lab), c in zip(cases, COLORS):
        alpha = 0.0 if vis is None else 3.912 / vis   # Koschmieder 근사 [1/m]
        p = 10 * np.log10(1 / r**2 * np.exp(-2 * alpha * r))
        ax.plot(r, p, color=c, lw=2, label=lab)
        ok = r[p >= p_thr]
        if ok.size:
            ax.plot(ok[-1], p_thr, "o", color=c)
    ax.axhline(p_thr, color=GRAY, ls="--", lw=1)
    ax.text(205, p_thr + 2, "검출 문턱(가정)", fontsize=9.5, color=GRAY)
    ax.set_xlim(0, 250)
    ax.set_ylim(-90, 0)
    ax.set_xlabel("거리 [m]")
    ax.set_ylabel("상대 수신 전력 [dB]")
    ax.legend(loc="upper right")
    ax.set_title("안개 속 수신 전력 ∝ exp(−2αR)/R²: 최대 거리가 급격히 줄어든다", loc="left", fontsize=11)
    ax.text(3, -86, "α ≈ 3.912 / 가시거리 (Koschmieder 근사, 개념도)", fontsize=8.5, color=GRAY)
    out(fig, "fog-attenuation")


if __name__ == "__main__":
    setup()
    motion_distortion()
    fog_attenuation()
