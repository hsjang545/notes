"""sync-11-ros2-time 그림: ApproximateTimeSynchronizer 짝짓기 타임라인(합성), /clock 발행 주파수에 따른 now() 계단."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import itertools

import numpy as np
import matplotlib.pyplot as plt

from _style import setup, save, COLORS, GRAY

SLUG = "sync-11-ros2-time"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def _save(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def approx_sync(events: list[tuple[float, int, float]], slop: float, qsize: int) -> list[tuple[float, float]]:
    """파이썬 message_filters ApproximateTimeSynchronizer.add()의 흐름을 두 토픽으로 단순화해 재현.
    events: (도착 시각, 토픽 번호, stamp). 반환: 짝지어진 (stamp0, stamp1) 목록."""
    queues: list[dict[float, None]] = [{}, {}]
    pairs: list[tuple[float, float]] = []
    for _, i, st in sorted(events):
        q = queues[i]
        q[st] = None
        while len(q) > qsize:
            del q[min(q)]
        other = queues[1 - i]
        cands = sorted((s for s in other if abs(s - st) <= slop), key=lambda s: abs(s - st))
        for s in itertools.islice(cands, None):
            if abs(s - st) < slop:
                pair = (st, s) if i == 0 else (s, st)
                pairs.append(pair)
                del q[st]
                del other[s]
                break
    return pairs


def matching_timeline() -> None:
    rng = np.random.default_rng(2)
    cam = np.arange(0, 0.6, 1 / 30) + 0.004
    lid = np.arange(0, 0.6, 0.1) + 0.012 + rng.normal(0, 0.002, 6)
    events = [(s + 0.015 + rng.uniform(0, 0.004), 0, s) for s in cam]
    events += [(s + 0.120 + rng.uniform(0, 0.01), 1, s) for s in lid]  # 라이다는 150 ms 가까이 늦게 도착
    fig, axes = plt.subplots(2, 1, figsize=(8.8, 4.6), sharex=True)
    for ax, (qsize, slop, title) in zip(axes, [(10, 0.015, "queue_size=10, slop=15 ms: 라이다 스캔마다 가장 가까운 프레임과 짝"),
                                               (2, 0.015, "queue_size=2: 라이다가 도착할 때 짝이 될 카메라 프레임이 이미 밀려남")]):
        pairs = approx_sync(events, slop, qsize)
        used_cam = {p[0] for p in pairs}
        used_lid = {p[1] for p in pairs}
        ax.scatter(cam * 1e3, np.ones_like(cam), marker="|", s=250, lw=2,
                   c=[COLORS[0] if s in used_cam else "#C7CDD4" for s in cam])
        ax.scatter(lid * 1e3, np.zeros_like(lid), marker="|", s=250, lw=2,
                   c=[COLORS[1] if s in used_lid else "#C7CDD4" for s in lid])
        for c_st, l_st in pairs:
            ax.plot([c_st * 1e3, l_st * 1e3], [1, 0], color=COLORS[2], lw=1.5)
        ax.set_yticks([0, 1], ["라이다 10 Hz", "카메라 30 Hz"])
        ax.set_ylim(-0.5, 1.6)
        ax.grid(False, axis="y")
        ax.set_title(title, fontsize=10.5)
        ax.text(598, 1.35, f"짝 {len(pairs)}개 / 라이다 {len(lid)}개", ha="right", fontsize=9, color=GRAY)
    axes[-1].set_xlabel("header.stamp [ms]  (회색 = 짝을 못 찾은 메시지)")
    fig.suptitle("ApproximateTimeSynchronizer 짝짓기(합성 데이터 예시)", fontsize=12)
    fig.tight_layout()
    _save(fig, "approx-sync-timeline")


def clock_staircase() -> None:
    t = np.linspace(0, 0.2, 2001)  # 재생 기준 실제 경과 [s]
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.plot(t * 1e3, t * 1e3, color=GRAY, ls="--", lw=1, label="bag 수신 시각(이상적인 시간)")
    for c, hz in zip([COLORS[1], COLORS[0]], [40, 200]):
        now = np.floor(t * hz) / hz
        ax.step(t * 1e3, now * 1e3, where="post", color=c, lw=1.8, label=f"--clock {hz}: now()는 {1000 / hz:g} ms 계단")
    ax.set_xlabel("재생 중 실제 경과 [ms]")
    ax.set_ylabel("노드의 now() [ms]")
    ax.set_title("/clock 발행 주파수가 now()의 분해능을 정한다")
    ax.legend(loc="upper left", fontsize=9)
    _save(fig, "clock-staircase")


if __name__ == "__main__":
    setup()
    matching_timeline()
    clock_staircase()
