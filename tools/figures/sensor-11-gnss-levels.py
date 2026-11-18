"""sensor-11-gnss-levels 그림: 정확도 단계 사다리, RTCM 3 MSM 데이터량과 직렬 통신 속도."""

import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E401,E702
from _style import setup, save, COLORS, GRAY  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

SLUG = "sensor-11-gnss-levels"
PREVIEW = os.environ.get("FIG_PREVIEW_DIR")


def out(fig: plt.Figure, name: str) -> None:
    if PREVIEW:
        fig.savefig(os.path.join(PREVIEW, f"{SLUG}-{name}.png"), dpi=80, bbox_inches="tight")
    save(fig, SLUG, name)


def level_ladder() -> None:
    # (단계, 대표 범위 m) — 본문 "단계 한눈에 보기" 표와 같게 둔다.
    rows = [
        ("1. 단독 측위", 1.0, 5.0),
        ("2. SBAS", 0.5, 1.5),
        ("3. DGPS", 0.3, 1.0),
        ("4. RTK float", 0.1, 1.0),
        ("5. RTK fixed", 0.01, 0.03),
        ("PPP(수렴 후)", 0.03, 0.2),
    ]
    # 한 상용 GNSS/INS 매뉴얼의 수평 위치 사양: SPS 1.5 m CEP, SBAS 0.6 m CEP, DGPS 0.4 m CEP, RTK 0.01 m 1σ, PPP 0.03 m CEP
    spec = {0: 1.5, 1: 0.6, 2: 0.4, 4: 0.01, 5: 0.03}
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    for i, (name, lo, hi) in enumerate(rows):
        ax.barh(i, hi - lo, left=lo, height=0.5, color=COLORS[i], alpha=0.8)
        if i in spec:
            ax.plot(spec[i], i, marker="D", color="black", ms=6, zorder=3)
    ax.plot([], [], "D", color="black", ms=6, label="한 상용 GNSS/INS 사양값(개활지)")
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(0.005, 10)
    ax.set_xticks([0.01, 0.1, 1, 10], ["1 cm", "10 cm", "1 m", "10 m"])
    ax.set_xlabel("수평 위치 정확도(대표 범위, 로그 축)")
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.legend(loc="lower right", fontsize=9)
    ax.set_title("GPS 정확도 단계: 보정을 더할수록 한 자릿수씩 좋아진다", loc="left", fontsize=11)
    out(fig, "level-ladder")


def msm_bytes(n_sat: int, n_sig: int, msm: int) -> float:
    """RTCM 3 MSM 메시지 하나의 바이트 수(프레임 6바이트 포함). 위성마다 같은 수의 신호를 가정."""
    sat_bits = {4: 18, 7: 36}[msm]
    sig_bits = {4: 48, 7: 80}[msm]
    cells = n_sat * n_sig
    bits = 169 + cells + sat_bits * n_sat + sig_bits * cells
    return bits / 8 + 6


def serial_budget() -> None:
    # 가정: GPS 10, GLONASS 8, Galileo 8, BeiDou 10기, 위성당 2주파, 1 Hz. 기준국 정보 메시지는 뺐다.
    sats = [10, 8, 8, 10]
    msm4 = sum(msm_bytes(n, 2, 4) for n in sats)
    msm7 = sum(msm_bytes(n, 2, 7) for n in sats)
    msm7_3f = sum(msm_bytes(n, 3, 7) for n in sats)
    bauds = [4800, 9600, 19200, 38400, 57600, 115200]
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    ax.bar(range(len(bauds)), [b / 10 for b in bauds], color=COLORS[0], alpha=0.8, width=0.6)
    for x, b in enumerate(bauds):
        ax.text(x, b / 10 * 1.12, f"{b / 10:,.0f} B/s", ha="center", fontsize=9)
    lines = [(msm4, "MSM4, 4개 시스템 2주파", COLORS[2]), (msm7, "MSM7, 4개 시스템 2주파", COLORS[1]),
             (msm7_3f, "MSM7, 4개 시스템 3주파", COLORS[3])]
    for y, lab, c in lines:
        ax.axhline(y, color=c, lw=1.6, ls="--", label=f"{lab} ≈ {y:,.0f} B/s")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_xticks(range(len(bauds)), [f"{b}" for b in bauds])
    ax.set_xlabel("직렬 통신 속도 [baud] (8N1: 1바이트 = 10비트)")
    ax.set_yscale("log")
    ax.set_ylim(200, 30000)
    ax.set_ylabel("초당 바이트 [B/s]")
    ax.grid(axis="x", visible=False)
    ax.set_title("RTCM 3 MSM 보정 데이터량(1 Hz 계산 예)과 직렬 처리량", loc="left", fontsize=11)
    out(fig, "serial-budget")
    print(f"MSM4 {msm4:.0f} B/s, MSM7 {msm7:.0f} B/s, MSM7 3f {msm7_3f:.0f} B/s")


if __name__ == "__main__":
    setup()
    level_ladder()
    serial_budget()
