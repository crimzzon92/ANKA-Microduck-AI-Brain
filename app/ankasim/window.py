"""Anka's ONE window in the 3D simulator (2026-11-11): the room from above and his own floor plan on top, his camera and
depth sensor and the last lines of the log below - scaled to fit the screen.

The window runs in its OWN program (ankasim/eyes.py --one-window, started by "Start everything.command"), so drawing it
never slows his brain or his walking commands down, and his camera is shown live. Anka's program only hands over what
it alone knows, through small files next to this one, a few times a second:
    live_room.jpg   the room picture (as the room window used to show it)
    live_room.json  where the mute button is in that picture
    live_log.txt    the last lines of the log
    live_cmd.txt    written by the window when you click the mute button (or press M); Anka's program reads it
    live_status.txt what "Start everything" is doing while it starts (the window shows it until Anka is awake)
This file has the drawing that both programs share.
"""
import os
import re
import subprocess
import sys
import textwrap

import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE_ROOM = os.path.join(HERE, "live_room.jpg")
LIVE_INFO = os.path.join(HERE, "live_room.json")
LIVE_LOG = os.path.join(HERE, "live_log.txt")
LIVE_CMD = os.path.join(HERE, "live_cmd.txt")
LIVE_STATUS = os.path.join(HERE, "live_status.txt")   # "seconds|what is happening" lines, written while starting

SYMBOLS = [("💭", "thinks:"), ("🦆", "says:"), ("❤️", "feels:"), ("🫀", "body:"), ("🦶", "move:"), ("😮", "surprised:"),
           ("🧑", ""), ("🎬", "script:"), ("🦉", "wise brain:"), ("🔎", "checked:"), ("📔", "diary:"), ("🎯", "goal:"),
           ("🏁", "goal done:"), ("🫳", "gave up:"), ("🧭", "mindful:"), ("🖼️", "kept a picture:"), ("🗺️", "map:"),
           ("🔊", "sound:"), ("👀", "sees:"), ("😴", ""), ("🌙", "night:"), ("🪞", "new about me:"), ("📝", "lesson:"),
           ("💡", "idea:"), ("🌀", "urge:")]
COLOURS = {"thinks:": (230, 200, 150), "says:": (120, 230, 255), "feels:": (170, 140, 255), "body:": (230, 150, 90),
           "move:": (150, 220, 150), "surprised:": (90, 160, 255), "script:": (200, 200, 200)}
BG = 24


def plain(line):
    """A log line in plain letters (the window's font has no emoji), with a word for the symbol it started with."""
    line = line.strip()
    label = None
    for sym, word in SYMBOLS:
        if line.startswith(sym):
            line, label = line[len(sym):].strip(), word
            break
    for a, b in (("–", "-"), ("—", "-"), ("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("→", "->"), ("…", "..."),
                 ("°", " deg"), ("·", "|"), ("×", "x")):
        line = line.replace(a, b)
    line = line.encode("ascii", "ignore").decode().strip()
    line = re.sub(r"\s{2,}", "  ", line)
    return ((label + " ") if label else "") + line, label


_log_cache = {"key": None, "img": None}


# 2026-11-13: easier to see what is what - a coloured tag in front of each line, what he SAYS and THINKS (and what you
# say) bright, the rest (body, moves, what he sees, the script...) dim, and a little space between the entries.
#            label         tag        tag colour (BGR)   text colour        important
KINDS = {"says:":       ("SAYS",    (60, 200, 255),   (150, 235, 255),  True),
         "thinks:":     ("THINKS",  (235, 170, 90),   (245, 215, 170),  True),
         "you:":        ("YOU",     (230, 230, 230),  (255, 255, 255),  True),
         "feels:":      ("FEELS",   (190, 120, 255),  (200, 170, 240),  False),
         "surprised:":  ("SURPRISE", (80, 150, 255),  (170, 200, 255),  True),
         "wise brain:": ("WISE",    (200, 200, 120),  (210, 210, 170),  False),
         "goal:":       ("GOAL",    (120, 210, 120),  (180, 220, 180),  False),
         "goal done:":  ("GOAL",    (120, 210, 120),  (180, 220, 180),  False),
         "idea:":       ("IDEA",    (120, 210, 120),  (180, 220, 180),  False),
         "urge:":       ("WANTS",   (150, 120, 255),  (200, 185, 245),  False)}
DIM_TAGS = {"body:": "body", "move:": "move", "sees:": "sees", "script:": "script", "mindful:": "mind",
            "diary:": "diary", "sound:": "sound", "map:": "map", "checked:": "check", "kept a picture:": "picture",
            "gave up:": "goal", "night:": "night", "new about me:": "me", "lesson:": "lesson"}
DIM = (125, 125, 125)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def _entry(raw):
    """(tag, tag colour, text, text colour, important) for one log line, or None to leave it out."""
    line = raw.strip()
    if line.startswith("\U0001f9d1"):                  # the person talking to him ("You: ...")
        text, label = plain(line)
        text = re.sub(r"^(You|you):\s*", "", text)
        text = re.sub(r"\s*\(sounded: [^)]*\)\s*$", "", text)
        return ("YOU", KINDS["you:"][1], text, KINDS["you:"][2], True)
    text, label = plain(line)
    if label:
        text = text[len(label):].strip()
    text = re.sub(r"\s*\d+(\.\d+)?s\s*$", "", text)          # the thinking time at the end
    text = re.sub(r"^\(thinking\)\s*", "", text)
    text = text.replace("decided to stay quiet", "(quiet)")
    m = re.fullmatch(r"\((?:Anka|body|inner urge):\s*(.*)\)", text)   # "(Anka: look around -> ...)" -> "look around -> ..."
    if m:
        text = m.group(1)
    if not text:
        return None
    if label == "script:" and re.search(r"\]\s+you say", text):
        return None                                     # the same words come again as "YOU"
    if label in KINDS:
        tag, tc, xc, imp = KINDS[label]
        return (tag, tc, text, xc, imp)
    return (DIM_TAGS.get(label, ""), DIM, text, DIM, False)


def log_panel(lines, w, h, k=1.0):
    """The last log lines: a coloured tag in front, the important ones bright, word-wrapped (redrawn only when
    something changed)."""
    key = (w, h, k, len(lines), lines[-1] if lines else "")
    if _log_cache["key"] == key:
        return _log_cache["img"]
    img = np.full((h, w, 3), BG, np.uint8)
    cv2.putText(img, "what is happening", (12, int(22 * k)), FONT, 0.5 * k, (150, 150, 150), 1, cv2.LINE_AA)
    tag_w, x0, step = int(70 * k), 12, int(18 * k)      # (2026-11-18: k = text size, bigger in the big window)
    cols = max(20, int((w - tag_w - x0 - 8) / (7.3 * k)))
    entries = []                                        # (rows, tag, tag colour, text colour, important)
    for raw in list(lines)[-40:]:
        e = _entry(raw)
        if e:
            tag, tc, text, xc, imp = e
            entries.append((textwrap.wrap(text, cols) or [""], tag, tc, xc, imp))
    # fit from the newest backwards
    y_room, keep = h - int(30 * k), []
    for e in reversed(entries):
        need = len(e[0]) * step + int(6 * k)
        if need > y_room and keep:
            break
        keep.append(e)
        y_room -= need
    y = int(44 * k)
    for rows, tag, tc, xc, imp in reversed(keep):
        if imp:                                         # a soft band behind what he says and thinks
            cv2.rectangle(img, (4, y - int(14 * k)), (w - 4, y + (len(rows) - 1) * step + int(6 * k)), (40, 40, 40), -1)
            cv2.rectangle(img, (4, y - int(14 * k)), (int(4 + 3 * k), y + (len(rows) - 1) * step + int(6 * k)), tc, -1)
        if tag:
            cv2.putText(img, tag, (x0, y), FONT, 0.42 * k, tc, 2 if imp else 1, cv2.LINE_AA)
        for i, row in enumerate(rows):
            cv2.putText(img, row, (x0 + tag_w, y + i * step), FONT, (0.45 if imp else 0.42) * k, xc, 1, cv2.LINE_AA)
        y += len(rows) * step + int(6 * k)
    _log_cache.update(key=key, img=img)
    return img


def fit(img, w, h):
    """Scales a picture to fit inside w x h (keeping its shape), top left on a dark background."""
    out = np.full((h, w, 3), BG, np.uint8)
    if img is None or img.size == 0:
        return out
    f = min(w / img.shape[1], h / img.shape[0])
    small = cv2.resize(img, (max(1, int(img.shape[1] * f)), max(1, int(img.shape[0] * f))), interpolation=cv2.INTER_LINEAR)
    out[:small.shape[0], :small.shape[1]] = small
    return out


_SCREEN = []


def _mac_screen():
    """On a Mac: the usable part of the screen (without the menu bar and the Dock) in PICTURE pixels. A Retina screen
    shows one picture pixel per screen pixel, and has 2 screen pixels per point - so a window measured in points came
    out half as big as meant (2026-11-12: "the window is too small")."""
    js = ("ObjC.import('AppKit'); var s = $.NSScreen.mainScreen; var f = s.visibleFrame;"
          "f.size.width + ',' + f.size.height + ',' + s.backingScaleFactor")
    out = subprocess.run(["osascript", "-l", "JavaScript", "-e", js], capture_output=True, text=True, timeout=5).stdout
    w, h, k = [float(v) for v in out.strip().split(",")[:3]]
    return int(w * k), int((h - 30) * k)          # (30 points for the window's own title bar)


def screen():
    """The screen size the window fits into, in picture pixels. On a Mac it is measured; elsewhere ANKA_SCREEN
    ("width,height", set by the start menu) or a guess."""
    if not _SCREEN:
        size = None
        if sys.platform == "darwin":
            try:
                size = _mac_screen()
            except Exception:
                size = None
        if size is None:
            try:
                size = tuple(int(float(v)) for v in os.environ.get("ANKA_SCREEN", "1440,860").split(",")[:2])
            except Exception:
                size = (1440, 860)
        _SCREEN.append(size)
    return _SCREEN[0]


def read_status():
    """The start steps from live_status.txt: [(seconds since the epoch, text), ...]."""
    steps = []
    try:
        with open(LIVE_STATUS, encoding="utf-8") as f:
            for line in f:
                t, _, text = line.strip().partition("|")
                if text:
                    steps.append((float(t), text))
    except (OSError, ValueError):
        pass
    return steps


def waiting_room(w=936, h=460, steps=None, now=None):
    """Shown until the first room picture arrives (2026-11-13: it took a minute before anything happened and it
    looked broken) - what is starting, step by step, and how long it has taken so far."""
    import time as _time
    now = now or _time.time()
    img = np.full((h, w, 3), 245, np.uint8)
    dark, grey, green = (60, 60, 60), (130, 130, 130), (60, 150, 60)
    cv2.putText(img, "Anka is waking up" + "." * (int(now * 2) % 4), (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.3, dark, 2,
                cv2.LINE_AA)
    steps = steps if steps is not None else read_status()
    if steps:
        secs = int(now - steps[0][0])
        cv2.putText(img, f"{secs // 60}:{secs % 60:02d}", (w - 130, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.1, grey, 2,
                    cv2.LINE_AA)
    y = 130
    for i, (t, text) in enumerate(steps[-8:]):
        last = i == len(steps[-8:]) - 1
        mark, colour = ("...", dark) if last else ("done", green)
        cv2.putText(img, mark, (40, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, colour, 2 if last else 1, cv2.LINE_AA)
        cv2.putText(img, text, (110, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, colour, 2 if last else 1, cv2.LINE_AA)
        y += 36
    cv2.putText(img, "This takes about a minute. Everything starts by itself - nothing is wrong.", (40, h - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, grey, 1, cv2.LINE_AA)
    return img


def _depth_colour(d):
    """Near = red, far = green (like the camera overlay)."""
    t = max(0.0, min(1.0, (d - 0.15) / 1.5))
    return (int(40 + 60 * t), int(60 + 170 * t), int(230 - 170 * t))


def _depth_grid(tof, side, k):
    """2026-11-18: the depth sensor's 8x8 zones with their distance in cm, side x side pixels."""
    img = np.full((side, side, 3), BG, np.uint8)
    cv2.putText(img, "depth sensor (cm)", (4, int(18 * k)), FONT, 0.45 * k, (150, 150, 150), 1, cv2.LINE_AA)
    top = int(28 * k)
    cell = (side - top - 4) // 8
    for r in range(8):
        for c in range(8):
            x1, y1 = 4 + c * cell, top + r * cell
            d = float("nan") if tof is None else float(tof["m"][r, c])
            colour = (50, 50, 50) if d != d else _depth_colour(d)
            cv2.rectangle(img, (x1, y1), (x1 + cell - 2, y1 + cell - 2), colour, -1)
            if d == d:
                cv2.putText(img, f"{d * 100:.0f}", (x1 + 3, y1 + cell // 2 + int(5 * k)), FONT, 0.33 * k,
                            (20, 20, 20), 1, cv2.LINE_AA)
    return img


def _facts_panel(eyes, w, h, k=1.0):
    """The numbers (connection, odometry, head, depth, what he finds) on the left, the depth sensor's grid on the right,
    and the key help, in a w x h panel."""
    out = np.full((h, w, 3), BG, np.uint8)
    side = min(h - int(24 * k), w // 2)
    if side > 60:
        g = _depth_grid(eyes.get("tof"), side, k)
        out[:side, w - side - 6:w - 6] = g
    text_w = w - side - 18
    cv2.putText(out, "his body's numbers", (14, int(22 * k)), FONT, 0.5 * k, (150, 150, 150), 1, cv2.LINE_AA)
    y, step = int(48 * k), int(22 * k)
    scale = 0.46 * k
    for text, colour in eyes.get("facts", []):
        if y > h - int(30 * k):
            break
        while text and cv2.getTextSize(text, FONT, scale, 1)[0][0] > text_w:   # (cut what doesn't fit beside the grid)
            text = text[:-1]
        cv2.putText(out, text, (14, y), FONT, scale, colour, 1, cv2.LINE_AA)
        y += step
    if eyes.get("help"):
        cv2.putText(out, eyes["help"], (10, h - int(10 * k)), FONT, 0.36 * k, (140, 140, 140), 1, cv2.LINE_AA)
    return out


def _window_size():
    """How much of the screen the window may use (ANKA_WINDOW_SIZE, default 0.8 = 80 %, 2026-11-18)."""
    try:
        return max(0.3, min(1.0, float(os.environ.get("ANKA_WINDOW_SIZE", "0.8"))))
    except ValueError:
        return 0.8


def layout(room, eyes, lines):
    """The whole window. Returns (picture, scale of the room picture, its x offset) - for the mute button.
    2026-11-18 (eyes given as a dict): drawn at 80 % of the screen, in two columns that fill it -
      left:  the room from above + his own floor plan, and below it his camera, both as wide as the column
             (the retail duck's camera is a wide 16:9 picture - before, it was squeezed into a small corner)
      right: the log on top, his body's numbers below."""
    room = room if room is not None else waiting_room()
    if isinstance(eyes, dict):
        sw, sh = screen()
        k = _window_size()
        W, H = int(sw * k), int(sh * k)
        rh, rw = room.shape[:2]
        cam = eyes.get("cam")
        cam_ratio = (cam.shape[0] / cam.shape[1]) if cam is not None and cam.size else 9 / 16
        left_w = int(min(W * 0.66, H / (rh / rw + cam_ratio)))      # room + camera fill the column's height
        right_w = W - left_w
        whole = np.full((H, W, 3), BG, np.uint8)
        s = left_w / rw
        room_s = cv2.resize(room, (left_w, max(1, int(rh * s))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
        whole[:room_s.shape[0], :left_w] = room_s
        cam_h = H - room_s.shape[0]
        if cam is not None and cam.size and cam_h > 20:
            f = min(left_w / cam.shape[1], cam_h / cam.shape[0])
            small = cv2.resize(cam, (max(1, int(cam.shape[1] * f)), max(1, int(cam.shape[0] * f))),
                               interpolation=cv2.INTER_AREA if f < 1 else cv2.INTER_LINEAR)
            x0 = (left_w - small.shape[1]) // 2
            y0 = room_s.shape[0] + (cam_h - small.shape[0]) // 2
            whole[y0:y0 + small.shape[0], x0:x0 + small.shape[1]] = small
        tk = max(1.0, H / 760)                       # text size: grows with the window (2026-11-18: "make the text bigger")
        facts_h = int(H * 0.36)
        whole[:H - facts_h, left_w:] = log_panel(lines, right_w, H - facts_h, tk)
        whole[H - facts_h:, left_w:] = _facts_panel(eyes, right_w, facts_h, tk)
        cv2.line(whole, (left_w, 0), (left_w, H), (60, 60, 60), 1)
        return whole, s, 0
    rh, rw = room.shape[:2]
    bottom_h = int(rh * 1.15)          # 2026-11-12: his eyes and the log a bit BIGGER than the room and the floor plan
    eyes_w = int(bottom_h * (eyes.shape[1] / eyes.shape[0])) if eyes is not None else int(rw * 0.5)
    eyes_w = min(eyes_w, int(rw * 0.55))
    whole = np.vstack([room, np.hstack([fit(eyes, eyes_w, bottom_h), log_panel(lines, rw - eyes_w, bottom_h)])])
    sw, sh = screen()
    f = _window_size() * min(sw / whole.shape[1], sh / whole.shape[0])
    if abs(f - 1.0) > 0.01:
        whole = cv2.resize(whole, (int(whole.shape[1] * f), int(whole.shape[0] * f)), interpolation=cv2.INTER_LINEAR)
    return whole, f, 0


def write_atomic(path, data):
    """Writes a file so the other program never reads half of it."""
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)
