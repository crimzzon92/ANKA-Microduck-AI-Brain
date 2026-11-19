"""Draws the charts of a progress report from its data files.

    python docs/progress/make_charts.py 2026-11-19

reads docs/progress/data/<date>/*.csv and writes the pictures to docs/progress/<date>/. Needs matplotlib
(pip install matplotlib). The numbers in the data files come from Anka's own test logs (tools/score_run.py and the
test suites' thought traces) - nothing here is estimated."""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATE = sys.argv[1] if len(sys.argv) > 1 else "2026-11-19"
DATA = os.path.join(HERE, "data", DATE)
OUT = os.path.join(HERE, DATE)
C1, C2, C3, MUTED = "#2f6fb0", "#d9822b", "#3a9a5b", "#b8b8b8"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e6e6e6", "axes.axisbelow": True, "figure.dpi": 140})


def rows(name):
    with open(os.path.join(DATA, name), newline="") as f:
        return list(csv.DictReader(f))


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), facecolor="white")
    plt.close(fig)


def short_date(d):
    return f"{int(d[5:7])}/{int(d[8:10])}"


def alone():
    r = rows("alone_steps.csv")
    x = range(len(r))
    labels = [f"{s['step']}\n" + s["label"].replace(" ", "\n", 1) for s in r]
    walk = [float(s["walked_m"]) for s in r]
    still = [float(s["still_pct"]) for s in r]
    split = next((i for i, s in enumerate(r) if s["setup"].startswith("3 days")), None)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.bar(x, walk, color=C1, width=0.6, label="Walked (m/day)")
    for i, v in enumerate(walk):
        ax.text(i, v + 0.4, f"{v:g}", ha="center", fontsize=9)
    ax.set_ylim(0, 25)
    ax.set_ylabel("metres walked per day")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8)
    ax2 = ax.twinx()
    ax2.plot(x, still, "-o", color=C2, label="Still (% of time)")
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("% of time standing still")
    ax2.spines["top"].set_visible(False)
    ax2.grid(False)
    if split:
        ax.axvline(split - 0.5, color="#999", ls="--", lw=1)
        ax.text(split - 0.55, 24, "← 1 day alone", ha="right", fontsize=8, color="#666")
        ax.text(split - 0.45, 24, "3 days alone →", fontsize=8, color="#666")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8, frameon=False, bbox_to_anchor=(0, 0.93))
    ax.set_title(f"Alone: how much he moves, step by step ({short_date(r[0]['date'])} → {short_date(r[-1]['date'])})", loc="left")
    save(fig, "alone_activity.png")

    fig, ax = plt.subplots(figsize=(9, 3.6))
    for k, c in (("happiness", C1), ("loneliness", C2), ("boredom", C3)):
        ax.plot(x, [float(s[k]) for s in r], "-o", color=c, label=k)
    if split:
        ax.axvline(split - 0.5, color="#999", ls="--", lw=1)
    ax.set_ylim(0, 1)
    ax.set_xticks(list(x))
    ax.set_xticklabels([s["step"] for s in r])
    ax.set_xlabel("step (same steps as above)")
    ax.legend(fontsize=8, frameon=False, ncol=3, loc="lower left")
    ax.set_title("Alone: how he feels (day average, 0–1)", loc="left")
    save(fig, "alone_feelings.png")


def stuck():
    s = rows("still_stretch.csv")
    f = rows("fixation.csv")
    fig, (a, c) = plt.subplots(1, 2, figsize=(9, 3.4))
    g = [r["group"] for r in s][::-1]
    m = [float(r["mean_s"]) for r in s][::-1]
    mx = [float(r["max_s"]) for r in s][::-1]
    a.barh(g, m, color=[C1] * (len(g) - 1) + [MUTED])
    a.set_xlim(0, max(m) * 1.35)
    for i, (v, w) in enumerate(zip(m, mx)):
        a.text(v + 2, i, f"{v:g} s (max {w:g})", va="center", fontsize=8)
    a.set_title("Longest still stretch alone (mean)", loc="left", fontsize=10)
    a.grid(axis="y", visible=False)
    xx = range(len(f))
    w_ = [float(r["with_pct"]) for r in f]
    wo = [float(r["without_pct"]) for r in f]
    c.bar([i - 0.18 for i in xx], w_, 0.36, color=C1, label="with")
    c.bar([i + 0.18 for i in xx], wo, 0.36, color=C2, label="without")
    for i in xx:
        c.text(i - 0.18, w_[i] + 1, f"{w_[i]:g}%", ha="center", fontsize=8)
        c.text(i + 0.18, wo[i] + 1, f"{wo[i]:g}%", ha="center", fontsize=8)
    c.set_xticks(list(xx))
    c.set_xticklabels([r["version"] for r in f])
    c.set_ylim(0, 65)
    c.legend(fontsize=8, frameon=False)
    c.set_title("Share of thoughts on one single thing", loc="left", fontsize=10)
    save(fig, "stuck.png")


def kick():
    k = rows("kick.csv")
    tries = [int(r["tries"]) for r in k]
    lined = [int(r["lined_up"]) for r in k]
    lost = [int(r["lost_in_approach"]) for r in k]
    pct = [100 * a / b for a, b in zip(lined, tries)]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.bar([r["round"] for r in k], pct, color=[MUTED] + [C1] * (len(k) - 1), width=0.55)
    for i, p in enumerate(pct):
        ax.text(i, p + 0.5, f"{lined[i]} of {tries[i]}", ha="center", fontsize=9)
        ax.text(i, -3.2, f"lost ball {lost[i]}×", ha="center", fontsize=8, color="#666")
    ax.set_ylim(-4, 25)
    ax.set_ylabel("% of tries lined up")
    ax.set_title(f"Kick in 3D: lined up with the ball, round by round ({short_date(k[0]['date'])}–{short_date(k[-1]['date'])})", loc="left")
    save(fig, "kick.png")


def lines(name, out, panels, mark=None):
    r = rows(name)
    d = [short_date(x["date"]) for x in r]
    fig, axes = plt.subplots(1, len(panels), figsize=(9, 3.2))
    for ax, (field, title, top) in zip(axes, panels):
        ax.plot(d, [float(x[field]) for x in r], "-o", color=C1)
        ax.set_ylim(0, top)
        ax.set_title(title, loc="left", fontsize=10)
        ax.tick_params(axis="x", labelsize=8)
    if mark:
        i = next((n for n, x in enumerate(r) if mark[0] in x["brain"]), None)
        if i:
            axes[0].axvline(i - 0.5, color="#999", ls="--", lw=1)
            axes[0].text(i - 0.4, panels[0][2] * 0.9, mark[1], fontsize=8, color="#666")
    save(fig, out)


def volume():
    r = rows("runs_per_day.csv")
    n = [int(x["runs"]) for x in r]
    fig, ax = plt.subplots(figsize=(9, 3.0))
    ax.bar([short_date(x["date"]) for x in r], n, color=C1, width=0.65)
    for i, v in enumerate(n):
        ax.text(i, v + 1, str(v), ha="center", fontsize=8)
    ax.tick_params(axis="x", labelsize=8)
    ax.set_ylim(0, max(n) * 1.13)
    ax.set_title(f"Measured runs per day – {sum(n)} in total", loc="left")
    save(fig, "test_volume.png")


def overview():
    """The whole development on one timeline: what he can do (top) and three key measures (bottom)."""
    import datetime as dt
    import matplotlib.dates as mdates
    P = lambda d: dt.datetime.strptime(d[:10], "%Y-%m-%d")
    ab = rows("abilities.csv")
    start, end = dt.datetime(2026, 10, 25), dt.datetime(2026, 11, 21)
    days = [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]
    areas = [("brain", "thinking & feeling", C1), ("memory", "memory & learning", C3), ("body", "body & senses", C2)]
    counts = {a: [sum(1 for r in ab if r["area"] == a and P(r["date"]) <= d) for d in days] for a, _, _ in areas}
    fig = plt.figure(figsize=(10, 7.2))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.55, 1], hspace=0.42, wspace=0.28)
    ax = fig.add_subplot(gs[0, :])
    ax.stackplot(days, [counts[a] for a, _, _ in areas], labels=[l for _, l, _ in areas], colors=[c for _, _, c in areas],
                 alpha=0.85, step="post")
    total = [sum(v) for v in zip(*counts.values())]
    ax.set_xlim(start, end)
    ax.set_ylim(0, max(total) * 1.45)
    ax.set_ylabel("things he can do")
    marks = [("2026-10-28", "brain starts"), ("2026-10-29", "2D body"), ("2026-11-02", "3D simulator"),
             ("2026-11-08", "feelings linger,\nsurprise"), ("2026-11-10", "living body,\non GitHub"),
             ("2026-11-11", "first kick"), ("2026-11-18", "memory & lessons\n(v0.3.0)"), ("2026-11-19", "taps, listens")]
    lift = [12, 34, 12, 40, 14, 44, 14, 44]          # (points above the line - staggered so labels never meet)
    side = [0, 0, 0, -18, 6, 10, -12, 0]
    for i, (d, label) in enumerate(marks):
        x = P(d)
        y = total[(x - start).days]
        ax.annotate(label, (x, y), xytext=(side[i], lift[i]), textcoords="offset points", ha="center", fontsize=8,
                    arrowprops=dict(arrowstyle="-", color="#999", lw=0.8))
    ax.text(end, total[-1], f"  {total[-1]}", va="center", fontsize=11, fontweight="bold")
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    ax.set_title("Anka's development so far – what he can do, and how well (all in simulation)", loc="left", fontsize=12)
    ax.text(1.0, -0.13, "next: the real Microduck, expected around March 2027 →", transform=ax.transAxes, ha="right",
            fontsize=8, color="#666")

    def small(pos, xs, ys, title, ylim, fmt, color=C1, note=None):
        a = fig.add_subplot(gs[1, pos])
        a.plot(xs, ys, "-o", color=color, ms=4)
        a.set_xlim(dt.datetime(2026, 11, 3), end)
        a.set_ylim(*ylim)
        a.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[5, 12, 19]))
        a.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
        a.tick_params(labelsize=8)
        a.set_title(title, loc="left", fontsize=9)
        a.annotate(fmt(ys[0]), (xs[0], ys[0]), xytext=(-4, 6), textcoords="offset points", ha="right", fontsize=8)
        a.annotate(fmt(ys[-1]), (xs[-1], ys[-1]), xytext=(4, 6), textcoords="offset points", fontsize=8, fontweight="bold")
        if note:
            a.text(0.02, 0.04, note, transform=a.transAxes, fontsize=7, color="#666")

    st = rows("alone_steps.csv")
    seen = {}
    xs = []
    for r in st:                                     # several steps on one day: spread them over that day
        n = seen.get(r["date"], 0)
        seen[r["date"]] = n + 1
        xs.append(P(r["date"]) + dt.timedelta(hours=12 + 3 * n))
    small(0, xs, [float(r["walked_m"]) for r in st], "Walked per day when alone (m)", (0, 25), lambda v: f"{v:g}",
          note="from Nov 18: 3 days alone (harder)")
    k = rows("kick.csv")
    seen, xs = {}, []
    for r in k:
        n = seen.get(r["date"], 0)
        seen[r["date"]] = n + 1
        xs.append(P(r["date"]) + dt.timedelta(hours=6 + 6 * n))
    small(1, xs, [100 * int(r["lined_up"]) / int(r["tries"]) for r in k], "Kick lined up with the ball (%)", (0, 25),
          lambda v: f"{v:.0f}%")
    m = rows("days_3d.csv")
    small(2, [P(r["date"]) for r in m], [float(r["map_error_cm"]) for r in m], "Own map error after a 3D day (cm)",
          (0, 33), lambda v: f"{v:g}", note="lower is better")
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, "overview.png"), facecolor="white", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    overview()
    alone()
    stuck()
    kick()
    lines("days_3d.csv", "body_3d.png", [("map_error_cm", "Map error after a 3D day (cm, lower is better)", 33),
                                         ("memory_variety", "Variety of what he remembers (0–1)", 0.65)])
    lines("cost_speed.csv", "cost_speed.png", [("cost_usd", "Cost of a 3D test day (USD)", 0.32),
                                               ("thought_s", "Seconds per thought in 3D", 18)],
          mark=("flash-lite", "cheaper day brain →"))
    volume()
    print("charts written to", OUT)
