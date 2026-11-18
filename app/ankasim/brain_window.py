"""ANKA's brain window (2026-11-18): a live picture of which parts of Anka are busy - its own window (OpenCV, like the
simulator's windows - no web browser), opened with the BRAIN VIEW button in the simulator (or the B key), or:
    ~/anka-env/bin/python ankasim/brain_window.py          (live)
    ~/anka-env/bin/python ankasim/brain_window.py --demo   (demo mode: Vision, Goals and Movement light up together)
Keys in the window: D = demo on/off, Q or Esc = close.

An organic net of small glowing neurons and fine connections fills the window - thick in places, thin in others. It is split into seven regions that blend
softly into each other at the borders: Vision (cyan), Attention (lavender), Goals (amber), Hearing & speech
(blue-white), Memory (rose), Feelings (coral), Movement (mint). The light comes from Anka's real activity -
viz/activity.json, written by anka/activity.py - and runs as a WAVE from a region's middle outwards (and a little way
into its neighbours): a brief event (a memory came up) sends one wave and fades back to the idle glow; ongoing activity
(walking) keeps sending waves while it runs. Asleep: everything dims and slow dream waves pass through Memory and
Feelings. It is its own program: it never slows Anka down, and Anka runs the same with it closed."""
import json
import math
import os
import sys
import time

import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
ACTIVITY = os.path.join(os.path.dirname(HERE), "viz", "activity.json")
TITLE = "ANKA brain"
W, H = 1180, 760                       # the picture (the window can be resized)
TOP, BOTTOM = 84, H - 120              # the net fills the space between the title and the legend
# id, name, colour (BGR for OpenCV), where the region's middle is (share of the net's width, height)
REGIONS = [("vision", "Vision", (243, 211, 95), (0.12, 0.28)), ("attention", "Attention", (255, 167, 185), (0.38, 0.22)),
           ("goals", "Goals", (91, 179, 242), (0.63, 0.24)), ("hearing", "Hearing & speech", (255, 220, 207), (0.89, 0.30)),
           ("memory", "Memory", (166, 138, 240), (0.22, 0.76)), ("feelings", "Feelings", (99, 122, 255), (0.52, 0.78)),
           ("movement", "Movement", (181, 224, 127), (0.80, 0.76))]
IDS = [r[0] for r in REGIONS]
SPACING = 16                           # typical pixels between neurons (smaller = denser)
ROUND = 2.6                            # the net's outline: 2 = an oval, higher = a rectangle with round corners
BLEND = 0.045                          # how far the regions blend into each other (share of the width)
IDLE = 0.16
WAVE_SPEED = 0.55                      # region radii per second
WAVE_WIDTH = 0.22
FADE = 2.2                             # seconds for a brief event's light to die away
SMOOTH = 0.15                          # seconds: how softly the light follows the activity (higher = softer)
FPS = 30                               # pictures per second
OPEN_SIZE = 0.5                        # the window's size when it opens (1.0 = 1180 x 760; it can be resized)
BRIGHT = 0.82                          # overall light strength (1.0 = the earlier, brighter look)


def _field(rng, n, sizes):
    """A smooth random 'landscape' over the window (a sum of soft blobs), scaled to 0..1."""
    cx, cy = rng.uniform(0, W, n), rng.uniform(TOP, BOTTOM, n)
    sx = rng.uniform(*sizes, n)
    sign = rng.choice([-1.0, 1.0], n, p=[0.35, 0.65])

    def at(x, y):
        x, y = np.asarray(x, float)[..., None], np.asarray(y, float)[..., None]
        return (sign * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sx ** 2))).sum(axis=-1)
    grid = at(*np.meshgrid(np.linspace(0, W, 60), np.linspace(TOP, BOTTOM, 30)))
    lo, hi = grid.min(), grid.max()
    return lambda x, y: np.clip((at(x, y) - lo) / (hi - lo), 0, 1)


def build():
    """A fixed (seeded) organic net filling the window: denser clusters, thinner stretches and a few small hollows,
    and a ragged outer edge - grown, not printed. Each neuron is linked to its near neighbours, and for every neuron
    we know how much it belongs to each region (soft at the borders)."""
    rng = np.random.default_rng(7)
    x0, x1, y0, y1 = 14, W - 14, TOP + 4, BOTTOM - 4
    mx, my, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    density = _field(rng, 34, (40, 150))                               # where it grows thick and where thin
    ragged = _field(rng, 40, (25, 70))                                 # makes the outer edge uneven
    pts, gap = [], []
    cell = SPACING * 0.5
    hashed = {}
    for x, y in zip(rng.uniform(x0, x1, 70000), rng.uniform(y0, y1, 70000)):
        u, v = (x - mx) / hw, (y - my) / hh                            # a rounded shape (a "squircle")...
        edge = (1 - (abs(u) ** ROUND + abs(v) ** ROUND) ** (1 / ROUND)) * hh
        fade = np.clip((edge + (float(ragged(x, y)) - 0.5) * 40) / 45, 0, 1)   # ...with a softly uneven edge
        dens = float(density(x, y)) ** 1.5 * fade
        if dens < 0.05:
            continue
        r = SPACING * (0.5 + 1.4 * (1 - dens))                        # thick places: neurons sit closer
        gx, gy = int(x // cell), int(y // cell)
        reach = int(r // cell) + 1
        ok = True
        for i in range(gx - reach, gx + reach + 1):
            for j in range(gy - reach, gy + reach + 1):
                for k in hashed.get((i, j), ()):
                    if (pts[k][0] - x) ** 2 + (pts[k][1] - y) ** 2 < (min(r, gap[k])) ** 2:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
        if ok:
            hashed.setdefault((gx, gy), []).append(len(pts))
            pts.append((x, y))
            gap.append(r)
    pts, gap = np.array(pts), np.array(gap)
    centres = np.array([(x0 + c[0] * (x1 - x0), y0 + c[1] * (y1 - y0)) for *_, c in REGIONS])
    dist = np.linalg.norm(pts[:, None, :] - centres[None, :, :], axis=2) / (x1 - x0)   # (nodes, regions)
    near = dist - dist.min(axis=1, keepdims=True)
    weight = np.exp(-near / BLEND)                                      # 1 for its own region, less for neighbours
    weight /= weight.sum(axis=1, keepdims=True)
    rad = dist / 0.24                                                   # 0 = a region's middle, ~1 = its edge
    d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
    np.fill_diagonal(d, 1e9)
    edges = set()
    for i in range(len(pts)):
        for j in np.argsort(d[i])[:rng.integers(2, 6)]:                 # some neurons have few links, some many
            if d[i, j] < 1.9 * max(gap[i], gap[j]):
                edges.add((min(i, j), max(i, j)))
        if rng.random() < 0.03:                                         # a few longer links
            j = int(np.argsort(d[i])[rng.integers(6, 16)])
            edges.add((min(i, j), max(i, j)))
    size = 0.9 + rng.random(len(pts)) ** 2 * 2.2                        # mostly small, a few bigger neurons
    phase = rng.random(len(pts)) * 6.28
    return pts.astype(int), weight, rad, np.array(sorted(edges)), size, phase, centres


PTS, WEIGHT, RAD, EDGES, SIZE, PHASE, CENTRES = build()
COL = np.array([r[2] for r in REGIONS], dtype=float)
NODE_COL = WEIGHT @ COL                                                 # colours blend at the borders
OWN = WEIGHT.argmax(axis=1)


def _cloud_maps(q=8):
    """For the soft background light: how much each small patch of the window belongs to each region."""
    ys, xs = np.mgrid[0:H // q, 0:W // q]
    p = np.stack([xs * q, ys * q], axis=-1).astype(float)
    dist = np.linalg.norm(p[:, :, None, :] - CENTRES[None, None, :, :], axis=-1) / (W - 52)
    w = np.exp(-(dist - dist.min(axis=-1, keepdims=True)) / (BLEND * 1.6))
    w /= w.sum(axis=-1, keepdims=True)
    return w * np.exp(-dist / 0.30)[..., :]                             # fades away from each middle


CLOUD = _cloud_maps()


def read_activity():
    try:
        with open(ACTIVITY) as f:
            return json.load(f)
    except Exception:
        return None


def demo_activity(now):
    """DEMO: every 10 s Vision, Goals and Movement light up together (6 s), with a memory and an attention flash."""
    cyc = now % 10.0
    start = now - cyc
    pulses = [{"r": "vision", "s": 1.0, "t": start + 0.1}, {"r": "goals", "s": 1.0, "t": start + 0.3},
              {"r": "attention", "s": 0.7, "t": start + 1.2}, {"r": "memory", "s": 0.9, "t": start + 6.8}]
    text = ("ANKA spots a sock." if cyc < 2 else "He wants to bring it to Alex." if cyc < 4 else
            "Walking to the sock..." if cyc < 6.5 else "Remembering where the sofa is.")
    return {"t": now, "pulses": pulses, "on": {"movement": 0.4 < cyc < 6.0, "vision": 0.4 < cyc < 6.0,
                                               "goals": 0.4 < cyc < 6.0}, "sleep": False, "text": text}


def intensities(act, now):
    """Brightness 0..1 for every neuron: idle glow + waves from pulses + continuous waves while something is on.
    Each region's light is worked out over the whole net and shared out by how much a neuron belongs to it, so the
    light flows softly over the borders."""
    excite = np.zeros((len(REGIONS), len(PTS)))                         # (regions, nodes), 0..1 above the idle glow
    if not act:
        return np.full(len(PTS), IDLE), excite.max(axis=1), False
    for p in act.get("pulses", []):
        if p.get("r") not in IDS:
            continue
        k, age = IDS.index(p["r"]), now - p.get("t", 0)
        if age < 0 or age > FADE * 2.5:
            continue
        front = WAVE_SPEED * age                                        # the wave runs from the middle outwards...
        wave = np.exp(-((RAD[:, k] - front) ** 2) / (2 * WAVE_WIDTH ** 2))
        glow = math.exp(-age / FADE)                                    # ...and the whole region glows, fading
        excite[k] = np.maximum(excite[k], p.get("s", 1.0) * np.clip(0.55 * glow + 0.9 * wave * glow ** 0.4, 0, 1))
    for rid, on in (act.get("on") or {}).items():
        if rid not in IDS or not on:
            continue
        k = IDS.index(rid)
        front = (now * WAVE_SPEED) % 1.6                                # waves keep coming while it runs
        wave = np.exp(-((RAD[:, k] - front) ** 2) / (2 * WAVE_WIDTH ** 2))
        excite[k] = np.maximum(excite[k], 0.55 + 0.45 * wave)
    asleep = bool(act.get("sleep"))
    if asleep:
        excite *= 0.5
        swing = (math.sin(now * 0.8) + 1) / 2
        front = (now * 0.25) % 1.4
        for rid, w in (("memory", swing), ("feelings", 1 - swing)):
            k = IDS.index(rid)
            excite[k] = np.maximum(excite[k], 0.5 * w * np.exp(-((RAD[:, k] - front) ** 2) / 0.08))
    lvl = IDLE * (0.6 if asleep else 1.0) + (1 - IDLE) * np.clip((WEIGHT.T * excite).sum(axis=0), 0, 1)
    return lvl, excite.max(axis=1), asleep


def draw(lvl, region_lvl, act, demo, stale, asleep, now):
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (20, 12, 9)
    L = np.clip(lvl * (0.90 + 0.10 * np.sin(now * 1.3 + PHASE)), 0, 1) * BRIGHT   # a slow, gentle twinkle
    # the soft background light: made small and scaled up
    reg = np.clip(region_lvl, 0, 1)
    cloud = (CLOUD * (0.05 + 0.22 * reg * BRIGHT)[None, None, :]) @ COL
    cloud = cv2.GaussianBlur(np.clip(cloud, 0, 255).astype(np.uint8), (0, 0), 2.0)
    img = cv2.add(img, cv2.resize(cloud, (W, H), interpolation=cv2.INTER_CUBIC))
    lines = np.zeros_like(img)
    for i, j in EDGES:                                                  # fine connections
        c = (NODE_COL[i] + NODE_COL[j]) / 2 * (0.10 + 0.60 * (L[i] + L[j]) / 2)
        cv2.line(lines, tuple(PTS[i]), tuple(PTS[j]), tuple(int(v) for v in c), 1, cv2.LINE_AA)
    img = cv2.add(img, lines)
    dots = np.zeros_like(img)
    whiten = NODE_COL + (255 - NODE_COL) * (L[:, None] * 0.45)          # bright neurons turn a little whiter
    colour = whiten * (0.28 + 0.72 * L[:, None])
    radius = np.maximum(1, np.round(SIZE * (0.7 + 1.0 * L))).astype(int)
    for n in range(len(PTS)):                                           # the neurons
        cv2.circle(dots, tuple(PTS[n]), int(radius[n]), tuple(int(v) for v in colour[n]), -1, cv2.LINE_AA)
    small = cv2.resize(dots, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    glow = cv2.resize(cv2.GaussianBlur(small, (0, 0), 1.8), (W, H), interpolation=cv2.INTER_LINEAR)
    img = cv2.add(img, cv2.convertScaleAbs(glow, alpha=1.6))           # the glow around bright neurons
    img = cv2.add(img, dots)
    # title, mode, legend, what he is doing
    band = img[:TOP - 10].astype(float) * 0.35                          # keep the title readable over the net
    img[:TOP - 10] = band.astype(np.uint8)
    img[BOTTOM + 8:] = (img[BOTTOM + 8:].astype(float) * 0.35).astype(np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "A.N.K.A.", (36, 56), font, 1.4, (245, 238, 230), 2, cv2.LINE_AA)
    mode = ("DEMO MODE - SIMULATED ACTIVITY" if demo else "LIVE - WAITING FOR ANKA" if stale else
            "LIVE - ASLEEP" if asleep else "LIVE")
    (mw, _), _ = cv2.getTextSize(mode, font, 0.5, 1)
    cv2.putText(img, mode, (W - mw - 36, 50), font, 0.5, (121, 212, 255) if demo else (196, 163, 143), 1, cv2.LINE_AA)
    cv2.line(img, (36, TOP - 10), (W - 36, TOP - 10), (56, 38, 29), 1)
    cv2.line(img, (36, BOTTOM + 8), (W - 36, BOTTOM + 8), (56, 38, 29), 1)
    x = 40
    for k, (_, name, col, _) in enumerate(REGIONS):                     # the legend - bright when the region is busy
        cv2.circle(img, (x, H - 80), 5, col, -1, cv2.LINE_AA)
        tc = (245, 240, 235) if region_lvl[k] > 0.35 else (189, 167, 154)
        cv2.putText(img, name, (x + 14, H - 74), font, 0.55, tc, 1, cv2.LINE_AA)
        (nw, _), _ = cv2.getTextSize(name, font, 0.55, 1)
        x += nw + 50
    text = ("ANKA is not running (start a simulation - this window shows him when he wakes up)." if stale and not demo
            else (act or {}).get("text") or "")
    text = text.encode("ascii", "ignore").decode()[:110]
    cv2.putText(img, text, (36, H - 36), font, 0.7, (240, 232, 226), 1, cv2.LINE_AA)
    cv2.putText(img, "D = demo on/off   Q = close", (W - 260, H - 12), font, 0.42, (120, 105, 95), 1, cv2.LINE_AA)
    return img


_child = {"p": None}


def launch():
    """Opens the brain window as its own program - unless it is already open. Used by the simulator's BRAIN VIEW
    button and its B key. Never raises: if it can't start, the simulator just goes on."""
    import subprocess
    try:
        p = _child["p"]
        if p is not None and p.poll() is None:
            return
        _child["p"] = subprocess.Popen([sys.executable, os.path.abspath(__file__)])
    except Exception as error:
        print(f"(can't open the brain window: {error})")


def main():
    demo = "--demo" in sys.argv
    cv2.namedWindow(TITLE, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(TITLE, int(W * OPEN_SIZE), int(H * OPEN_SIZE))   # drag the corner to make it bigger
    act, read_at = None, 0.0
    shown, shown_reg, last = None, None, time.time()                   # what is on screen glides towards the target
    while True:
        now = time.time()
        dt, last = now - last, now
        if demo:
            act, stale = demo_activity(now), False
        else:
            if now - read_at > 0.2:
                act, read_at = read_activity(), now
            stale = not act or now - act.get("t", 0) > 5
        lvl, reg, asleep = intensities(None if stale and not demo else act, now)
        if shown is None:
            shown, shown_reg = lvl, reg
        k = 1 - math.exp(-dt / SMOOTH)                                  # soft: light fades in and out, never jumps
        shown, shown_reg = shown + (lvl - shown) * k, shown_reg + (reg - shown_reg) * k
        cv2.imshow(TITLE, draw(shown, shown_reg, act, demo, stale, asleep, now))
        key = cv2.waitKey(max(1, int(1000 / FPS - (time.time() - now) * 1000))) & 0xFF
        if key in (ord("q"), ord("Q"), 27):
            break
        if key in (ord("d"), ord("D")):
            demo = not demo
        try:
            if cv2.getWindowProperty(TITLE, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if "--snapshot" in sys.argv:                                        # (for testing: one picture to a file, no window)
        out = sys.argv[sys.argv.index("--snapshot") + 1]
        t = float(sys.argv[sys.argv.index("--at") + 1]) if "--at" in sys.argv else time.time()
        demo = "--demo" in sys.argv
        act = demo_activity(t) if demo else read_activity()
        stale = not demo and (not act or t - act.get("t", 0) > 5)
        lvl, reg, asleep = intensities(None if stale else act, t)
        cv2.imwrite(out, draw(lvl, reg, act, demo, stale, asleep, t))
        print("wrote", out, "| neurons", len(PTS), "links", len(EDGES), "| region levels",
              {rid: round(float(reg[k]), 2) for k, rid in enumerate(IDS)})
    else:
        main()
