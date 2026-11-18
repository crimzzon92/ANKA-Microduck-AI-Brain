"""His FEELING LAYER (2026-11-15, plan step A): a small local model that can NOT see the room.

It gets only his feelings (in words), the big feelings that still linger, whether someone is with him, and its own
last two wishes - and writes what his feelings make him WANT right now, in a few words. It runs in its own thread on
its own clock (every URGE_EVERY seconds, and at once when a feeling jumps), so the wish lies ready when the next
thought starts and thinking is never slower. The thinking brain is told the wish as a fact about himself - what he
does is still its own choice. If Ollama or the model is missing, the layer just stays quiet.
"""
import json
import threading
import time
import urllib.request

from settings import URGE_EVERY, URGE_JUMP, URGE_MODE, URGE_MODEL
from anka.shared import awake, state

NAMES = {"curiosity": "curious", "boredom": "bored", "loneliness": "lonely", "happiness": "happy",
         "affection": "loving", "nervousness": "nervous", "playfulness": "playful"}
SYSTEM = ("You are the feelings inside a small duck robot called Anka. You cannot see or hear anything - you only "
          "feel. Say what these feelings make Anka WANT right now, in one short sentence in first person "
          "(at most 10 words), like an animal's urge. Only the wish, nothing else. Don't say please. "
          "Say what the strongest feeling wants NOW - it may be something different from a moment ago.")
_last = []          # its own last wishes (to say something new when the feelings changed)


def _level(v):
    return "a little" if v < 0.35 else "quite" if v < 0.7 else "very"


def feeling_words():
    from anka.feelings import feelings, feelings_lock, echo_text, RESTING
    with feelings_lock:
        f = dict(feelings)
        echo = echo_text()
    rest = lambda k: RESTING.get(k, (0.0, 0))[0]
    order = sorted(f.items(), key=lambda kv: -abs(kv[1] - rest(kv[0])))
    words = ", ".join(f"{_level(v)} {NAMES.get(k, k)}" for k, v in order if v >= 0.2)
    return f, words or "calm", echo


def prompt_text():
    from anka.thinking import is_alone
    _, words, echo = feeling_words()
    text = f"Anka feels: {words}."
    if echo:
        text += "\n" + echo.split(":\n", 1)[-1].strip()
    text += "\nHe is alone." if is_alone() else "\nSomeone he knows is with him."
    if _last:
        text += "\nWhat he wanted a moment ago: " + "; ".join(_last[-2:])
    return text + "\nWhat does Anka want right now?"


def ask_model(text):
    body = {"model": URGE_MODEL, "stream": False, "think": False, "keep_alive": "30m",
            "options": {"num_ctx": 1024, "num_predict": 30, "temperature": 0.8},
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]}
    req = urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        out = json.loads(r.read().decode())
    answer = " ".join(((out.get("message") or {}).get("content") or "").split()).strip().strip('"')
    return answer.splitlines()[0][:120] if answer else ""


def urge_loop():
    """Runs as long as Anka lives: a new wish every URGE_EVERY seconds, or at once when a feeling jumps."""
    from anka.trace import trace
    last_feel, last_t, quiet_until, said_missing = None, 0.0, 0.0, False
    while True:
        time.sleep(1.0)
        now = time.time()
        if not awake.is_set() or now < quiet_until:
            continue
        f, _, _ = feeling_words()
        jumped = last_feel is not None and max(abs(f[k] - last_feel.get(k, f[k])) for k in f) >= URGE_JUMP
        if now - last_t < URGE_EVERY and not jumped:
            continue
        text = prompt_text()
        t0 = time.time()
        try:
            wish = ask_model(text)
        except Exception as error:
            if not said_missing:
                print(f"🌀 (the feeling layer can't reach {URGE_MODEL} in Ollama: {str(error)[:80]} – "
                      f"install it with: ollama pull {URGE_MODEL})")
                said_missing = True
            quiet_until = now + 60
            continue
        last_feel, last_t = f, time.time()
        if not wish:
            continue
        _last.append(wish)
        del _last[:-2]
        state["urge"] = (time.time(), wish)
        print(f"🌀 (inner urge: {wish})")
        trace("urge", urge=wish, model=URGE_MODEL, seconds=round(time.time() - t0, 2), why="jump" if jumped else "time",
              feel={k: round(v, 2) for k, v in f.items()})


def start():
    if URGE_MODE == "local":
        threading.Thread(target=urge_loop, daemon=True).start()
        print(f"🌀 Feeling layer: {URGE_MODEL} on this Mac (only sees his feelings, never the room)")
