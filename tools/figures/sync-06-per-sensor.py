"""sync-06-per-sensor 그림: 카메라 노출·판독 타임라인, 라이다 위상과 카메라 트리거, 하한선 추정."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from _style import setup, save, COLORS, GRAY

PREVIEW = os.environ.get("FIG_PREVIEW_DIR")
SLUG = "sync-06-per-sensor"


def _save(fig, name):
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def camera_timeline() -> None:
    """롤링 셔터: 행 r의 노출 구간 [t0 + r·t_line, + T_exp]. 값(ms)은 예시."""
    t_trig, d_trig, t_exp, readout = 0.0, 0.5, 8.0, 20.0
    t0 = t_trig + d_trig
    rows = 1.0  # 정규화된 행 위치 0(맨 위)~1(맨 아래)
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    # 롤링 셔터 노출 영역(평행사변형)
    poly = Polygon([[t0, 0], [t0 + t_exp, 0], [t0 + t_exp + readout, rows], [t0 + readout, rows]],
                   closed=True, color=COLORS[0], alpha=0.25, label="노출 중인 행(롤링 셔터)")
    ax.add_patch(poly)
    ax.plot([t0 + t_exp, t0 + t_exp + readout], [0, rows], color=COLORS[0], lw=1.5,
            label="행 판독(노출 끝)")
    # 노출 중간선
    ax.plot([t0 + t_exp / 2, t0 + t_exp / 2 + readout], [0, rows], color=COLORS[2], lw=2, ls="--",
            label="행별 노출 중간 t_mid(r)")
    mid_c = t0 + t_exp / 2 + readout / 2
    ax.plot(mid_c, 0.5, "o", color=COLORS[2], ms=8, zorder=5)
    ax.annotate("프레임 대표 시각\n(가운데 행의 노출 중간)", xy=(mid_c, 0.5), xytext=(mid_c + 4, 0.2),
                fontsize=9, arrowprops=dict(arrowstyle="->", color=GRAY))
    # 주요 시각
    marks = [(t_trig, "트리거", COLORS[3], "right"), (t0, "노출 시작", COLORS[3], "left"),
             (t0 + t_exp + readout, "판독 끝", COLORS[0], "center"),
             (t0 + t_exp + readout + 12, "호스트 수신(예시)", COLORS[1], "center")]
    for x, lab, c, ha in marks:
        ax.axvline(x, color=c, lw=1, ls=":")
        ax.text(x + (0.3 if ha == "left" else -0.3 if ha == "right" else 0), -0.17, lab,
                ha=ha, va="bottom", fontsize=9, color=c)
    ax.annotate("", xy=(t0 + t_exp, -0.06), xytext=(t0, -0.06), arrowprops=dict(arrowstyle="<->", color=GRAY))
    ax.text(t0 + t_exp + 0.4, -0.06, "T_exp", ha="left", va="center", fontsize=9, color=GRAY)
    ax.annotate("", xy=(t0 + readout, 1.07), xytext=(t0, 1.07), arrowprops=dict(arrowstyle="<->", color=GRAY))
    ax.text(t0 + readout / 2, 1.1, "판독 시간 H·t_line", ha="center", va="top", fontsize=9, color=GRAY)
    ax.set_xlim(-2, 45)
    ax.set_ylim(1.2, -0.25)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_yticklabels(["첫 행", "가운데 행", "마지막 행"])
    ax.set_xlabel("트리거 기준 시간 [ms]")
    ax.set_title("롤링 셔터 카메라의 노출·판독과 타임스탬프 후보 (값은 예시)", pad=20)
    ax.legend(loc="upper right", fontsize=8.5, bbox_to_anchor=(1.0, 0.85))
    _save(fig, "camera-exposure-timeline")


def lidar_phase() -> None:
    """10 Hz 라이다 방위각(톱니)과 카메라 시야(±30°, 광축 90°), 노출 창."""
    T = 0.1
    t = np.linspace(0, 0.3, 3001)
    fig, axes = plt.subplots(2, 1, figsize=(7.6, 5.0), sharex=True)
    cases = [(0.0, "위상 고정: 초 경계에서 0° 통과"), (0.037, "위상 미고정: 위상이 임의(예: 37 ms 어긋남)")]
    t_trig, d_trig, t_exp = 0.02295, 50e-6, 4e-3
    mids = [t_trig + d_trig + t_exp / 2 + k * T for k in range(3)]
    for ax, (shift, title) in zip(axes, cases):
        az = ((t - shift) / T % 1.0) * 360.0
        az_plot = az.copy()
        az_plot[np.abs(np.diff(az, prepend=az[0])) > 180] = np.nan
        ax.plot(t * 1e3, az_plot, color=COLORS[0], lw=1.5, label="라이다 방위각")
        ax.axhspan(60, 120, color=COLORS[2], alpha=0.15, label="카메라 시야(60°~120°)")
        ax.axhline(90, color=COLORS[2], lw=0.8, ls="--")
        for m in mids:
            ax.axvspan((m - t_exp / 2) * 1e3, (m + t_exp / 2) * 1e3, color=COLORS[1], alpha=0.35)
        ax.plot([], [], color=COLORS[1], alpha=0.35, lw=6, label="카메라 노출 창")
        ax.set_ylim(0, 360)
        ax.set_yticks([0, 90, 180, 270, 360])
        ax.set_ylabel("방위각 [°]")
        ax.set_title(title, fontsize=10.5)
    axes[1].set_xlabel("PPS 초 경계 기준 시간 [ms]")
    fig.suptitle("라이다 회전 위상과 카메라 트리거 정렬 (10 Hz, 노출 4 ms, 예시)")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=9)
    _save(fig, "lidar-phase-trigger")


def lower_envelope() -> None:
    """내부 시계 τ와 수신 시각의 차이. 모의 데이터(오프셋 2 ms, 속도비 +30 ppm, 최소 지연 1.5 ms)."""
    rng = np.random.default_rng(2)
    tau = np.sort(rng.uniform(0, 120, 1600))
    delay = 1.5e-3 + rng.gamma(1.2, 0.4e-3, tau.size) + (rng.random(tau.size) < 0.03) * rng.uniform(2e-3, 8e-3, tau.size)
    host = 2e-3 + (1 + 30e-6) * tau + delay
    y = (host - tau) * 1e3
    window = 5.0
    edges = np.arange(tau[0], tau[-1] + window, window)
    idx = np.digitize(tau, edges)
    picks = [np.flatnonzero(idx == w)[np.argmin(y[idx == w])] for w in np.unique(idx)]
    b, a = np.polyfit(tau[picks], host[picks], 1)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.scatter(tau, y, s=4, color=COLORS[0], alpha=0.35, label="수신 시각 − 내부 시각", rasterized=True)
    ax.scatter(tau[picks], y[picks], s=22, color=COLORS[1], zorder=3, label="창(5 s)별 최소 샘플")
    tt = np.linspace(0, 120, 10)
    ax.plot(tt, (a + b * tt - tt) * 1e3, color=COLORS[1], lw=1.8, label="하한선 맞춤 a + b·τ")
    ax.plot(tt, (a + (1 + 0) * tt - tt) * 0 + (2e-3 + 30e-6 * tt + 1.5e-3) * 1e3, color="black", lw=1, ls="--",
            label="참 관계 + 최소 지연(모의 설정값)")
    ax.set_ylim(3, 9)
    ax.set_xlabel("센서 내부 시각 τ [s]")
    ax.set_ylabel("t_rx − τ [ms]")
    ax.set_title(f"하한선 추정 (모의 데이터): 추정 속도비 {(b - 1) * 1e6:+.1f} ppm, 설정값 +30 ppm")
    ax.legend(loc="lower right", fontsize=8.5)
    _save(fig, "lower-envelope")


if __name__ == "__main__":
    setup()
    camera_timeline()
    lidar_phase()
    lower_envelope()
