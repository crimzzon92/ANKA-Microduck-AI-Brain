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


if __name__ == "__main__":
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
