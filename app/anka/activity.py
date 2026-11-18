"""ANKA's live activity for the brain view (2026-11-18): which parts of him are busy right now - Vision, Attention, Goals,
Memory, Movement, Feelings, Hearing & speech - and whether he sleeps. Only for SHOWING (app/viz/index.html reads the
file viz/activity.json). Nothing here changes what he does; it never raises, and a background thread writes the file a
few times a second, so the thinking and the body never wait for it. With the view closed nothing changes for Anka."""
import json
import os
import threading
import time

REGIONS = ("vision", "attention", "goals", "memory", "movement", "feelings", "hearing")
FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "viz", "activity.json")

_lock = threading.Lock()
_state = {"pulses": [], "on": {}, "sleep": False, "text": "", "changed": True}
_started = [False]


def pulse(region, strength=1.0, text=None):
    """A brief event (a memory came up, a new thing seen): a short flash that fades back to the idle glow."""
    try:
        with _lock:
            _state["pulses"] = (_state["pulses"] + [{"r": region, "s": round(max(0.1, min(1.0, strength)), 2),
                                                     "t": round(time.time(), 2)}])[-40:]
            if text:
                _state["text"] = str(text)[:90]
            _state["changed"] = True
        _start()
    except Exception:
        pass


def set_on(region, on=True, text=None):
    """Ongoing activity (walking): lit while it runs."""
    try:
        with _lock:
            if bool(_state["on"].get(region)) != bool(on):
                _state["on"][region] = bool(on)
                _state["changed"] = True
            if text:
                _state["text"] = str(text)[:90]
                _state["changed"] = True
        _start()
    except Exception:
        pass


def set_sleep(asleep, text=None):
    set_on("_sleep", asleep, text)


def from_trace(kind, data):
    """Turns the thought log's events into activity (anka/trace.py calls this for every event, also outside tests)."""
    try:
        if kind == "thought":
            pulse("attention", 1.0 if data.get("think_level") == "wise" else 0.7,
                  text=data.get("thought"))
            if data.get("goal_events"):
                pulse("goals", 1.0)
            if data.get("speak") and str(data.get("speak")).lower() not in ("none", "null"):
                pulse("hearing", 0.8)
            if data.get("picture"):
                pulse("vision", 0.5)
            s = data.get("surprise")
            if isinstance(s, (int, float)) and s >= 0.4:
                pulse("feelings", s)
            r = data.get("restless")
            set_on("feelings_restless", isinstance(r, (int, float)) and r >= 0.5)
        elif kind in ("reply", "own_line"):
            if kind == "reply":
                pulse("hearing", 1.0, text=data.get("human"))          # someone talked to him...
            pulse("hearing", 0.9, text=data.get("answer") or data.get("text"))   # ...and he spoke
        elif kind in ("mood_memory", "old_memory", "assoc_memory", "lessons_shown"):
            pulse("memory", 0.8)
            if kind == "mood_memory":
                pulse("feelings", 0.5)
        elif kind in ("kick_result", "kick_approach"):
            pulse("movement", 1.0)
        elif kind.startswith("goal"):
            pulse("goals", 0.9)
    except Exception:
        pass


def _snapshot():
    with _lock:
        on = dict(_state["on"])
        snap = {"t": round(time.time(), 2), "pulses": list(_state["pulses"]), "sleep": bool(on.pop("_sleep", False)),
                "on": {"movement": bool(on.get("movement")),
                       "feelings": bool(on.get("feelings_restless"))},
                "text": _state["text"]}
        _state["changed"] = False
    return snap


def _writer():
    last = 0.0
    while True:
        time.sleep(0.25)
        try:
            with _lock:
                changed = _state["changed"]
            if not changed and time.time() - last < 1.0:
                continue
            data = json.dumps(_snapshot()).encode()
            os.makedirs(os.path.dirname(FILE), exist_ok=True)
            tmp = FILE + ".tmp"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, FILE)
            last = time.time()
        except Exception:
            time.sleep(2.0)


def _start():
    if not _started[0]:
        _started[0] = True
        threading.Thread(target=_writer, daemon=True).start()
