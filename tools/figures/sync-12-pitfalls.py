"""sync-12-pitfalls 그림: step과 slew가 기록 stamp에 남기는 흔적, 증상 모양별 오프셋 예(모두 합성)."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _style import setup, save, COLORS, GRAY

SLUG = "sync-12-pitfalls"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def _save(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def step_vs_slew() -> None:
    """10 Hz 센서, 시스템 시계가 실제보다 0.3 s 앞서 있다가 t=2 s에 보정."""
    t = np.arange(0, 6, 0.1)  # 실제 측정 시각
    err0, t_fix = 0.3, 2.0
    step = np.where(t < t_fix, err0, 0.0)
    rate = 0.1  # slew 속도 100,000 ppm 가정(그림을 보이게 하려는 과장값)
    slew = np.clip(err0 - rate * np.clip(t - t_fix, 0, None), 0, None)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9))
    for err, c, name in [(step, COLORS[1], "step(뒤로 0.3 s)"), (slew, COLORS[0], "slew(천천히 보정)")]:
        stamp = t + err
        axes[0].plot(t, stamp, ".", ms=4, color=c, label=name)
        axes[1].plot(t[1:], np.diff(stamp) * 1e3, "-o", ms=3, lw=1.2, color=c, label=name)
    axes[0].plot(t, t, color=GRAY, ls="--", lw=1, label="정상(stamp = 실제 시각)")
    axes[0].set_xlabel("실제 측정 시각 [s]")
    axes[0].set_ylabel("기록된 stamp [s]")
    axes[0].set_title("stamp: step은 되돌아가고 slew는 기울기만 바뀜")
    axes[0].legend(loc="upper left", fontsize=8.5)
    axes[1].axhline(100, color=GRAY, ls="--", lw=1)
    axes[1].set_xlabel("실제 측정 시각 [s]")
    axes[1].set_ylabel("연속 stamp 간격 [ms]")
    axes[1].set_title("간격: step은 음수 한 번, slew는 수 초간 짧아짐")
    axes[1].annotate("간격 = 100 − 300 = −200 ms\n(stamp 역행)", xy=(2.0, -200), xytext=(2.6, -150),
                     arrowprops=dict(arrowstyle="->", color=GRAY), fontsize=9)
    axes[1].set_ylim(-250, 160)
    fig.suptitle("시계 보정 방식이 10 Hz 센서 stamp에 남기는 흔적(합성 데이터 예시)", fontsize=12)
    fig.tight_layout()
    _save(fig, "step-vs-slew")


def symptom_shapes() -> None:
    rng = np.random.default_rng(4)
    t = np.arange(0, 600.0)
    fig, axes = plt.subplots(2, 2, figsize=(9.6, 5.6), sharex=True)
    # 1) 톱니: 두 데몬이 번갈아 조정
    saw = 2.0 * ((t % 64) / 64 - 0.5) + rng.normal(0, 0.05, t.size)
    axes[0, 0].plot(t, saw, color=COLORS[0], lw=1)
    axes[0, 0].set_title("톱니: 데몬 둘이 같은 시계를 조정", fontsize=10.5)
    axes[0, 0].set_ylabel("오프셋 [ms]")
    # 2) 부하 연동
    load = (t > 200) & (t < 400)
    ld = rng.normal(0, 0.3, t.size) + np.where(load, rng.normal(0, 6, t.size), 0)
    axes[0, 1].plot(t, ld, color=COLORS[1], lw=0.8)
    axes[0, 1].axvspan(200, 400, color=GRAY, alpha=0.1)
    axes[0, 1].text(300, 17, "부하 구간", ha="center", fontsize=9, color=GRAY)
    axes[0, 1].set_ylim(-22, 22)
    axes[0, 1].set_title("부하 때만 흔들림: PTP 미지원 스위치·SW 타임스탬프", fontsize=10.5)
    axes[0, 1].set_ylabel("오프셋 [µs]")
    # 3) 점프 후 느린 회복
    jr = rng.normal(0, 0.02, t.size) + np.where(t >= 250, 30 * np.exp(-(t - 250) / 60), 0)
    axes[1, 0].plot(t, jr, color=COLORS[3], lw=1)
    axes[1, 0].set_title("점프 뒤 서서히 회복: PHC 리셋, step 없는 재수렴", fontsize=10.5)
    axes[1, 0].set_ylabel("오프셋 [µs]")
    # 4) 한 방향으로 벌어짐
    dr = np.where(t >= 150, 0.05 * (t - 150), 0) + rng.normal(0, 0.3, t.size)
    axes[1, 1].plot(t, dr, color=COLORS[2], lw=1)
    axes[1, 1].axvline(150, color=GRAY, ls=":", lw=1)
    axes[1, 1].text(160, 18, "기준 상실", fontsize=9, color=GRAY)
    axes[1, 1].set_title("한 방향으로 벌어짐: 홀드오버, 엉뚱한 PHC", fontsize=10.5)
    axes[1, 1].set_ylabel("오프셋 [µs]")
    for ax in axes[1]:
        ax.set_xlabel("시간 [s]")
    fig.suptitle("오프셋 그래프 모양으로 함정 좁히기(합성 데이터 예시, 크기는 임의)", fontsize=12)
    fig.tight_layout()
    _save(fig, "symptom-shapes")


if __name__ == "__main__":
    setup()
    step_vs_slew()
    symptom_shapes()
