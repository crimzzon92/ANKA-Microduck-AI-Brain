"""Anka's WORKING MEMORY (2026-11-19, the author's idea: "two layers of memory, like a human brain").

Layer 1 is the long-term memory (anka/memory.py: diary, facts, conversations, lessons - searched by meaning, tidied at
night). Layer 2 is this: a short list (at most WM_MAX) of what is going on RIGHT NOW - what someone asked of him, what
he promised - kept in view in every thought and answer until it is done, together with what his body has done since.

He decides what goes in and when it is done: in an answer he writes HOLD: <it>, and later LETGO: <it>. Only what HE
agreed to or promised (2026-11-20: in the "will" test he refused "stand in the corner" but held it as an order, then
froze - an order he refused is not his to carry). Python only keeps
the list and adds facts (who said it, their words, how long ago, what his body did since, how far he is from where he
was then). Nothing here tells him what to do. Found in the "staylong" test (2026-11-19): he remembered Alex's request
for 20 minutes, but did not connect it with his own body walking 2.4 m to the window - the two facts were in different
places of what he sees. Here they stand together.

Switch: settings.WORKING_MEMORY (--no-working-memory = off). Kept only for the day: at night what is still open goes
into the diary ("Still open when I went to sleep: ...") and the list is emptied."""
import math
import re
import time

from settings import WORKING_MEMORY, WM_MAX, WM_MAX_AGE
from anka.shared import state

MOVE_WORDS = r"(?i)\b(walk|explore|go|step|bring|follow|carry|kick|pick|tap|come|move|waddle|run)\b"


def _ago(seconds):
    m = int(seconds // 60)
    return "just now" if m < 1 else "1 minute ago" if m == 1 else f"{m} minutes ago" if m < 90 else f"{m // 60} hours ago"


def _where():
    """His OWN idea of where he is (step counting in the 2D body), or None if this body has none."""
    try:
        from anka.body import body
    except Exception:
        return None
    for xa, ya in (("est_x", "est_y"), ("x", "y")):
        if body is not None and hasattr(body, xa) and hasattr(body, ya):
            try:
                return float(getattr(body, xa)), float(getattr(body, ya))
            except (TypeError, ValueError):
                return None
    return None


def items():
    """The open items, oldest first (old ones fall away after WM_MAX_AGE)."""
    now = time.time()
    wm = [i for i in state.get("wm", []) if now - i["t"] < WM_MAX_AGE]
    state["wm"] = wm
    return wm


def note_moves(log):
    """Every body step, with the time (called by run_act) - the facts 'since then your body ...' come from here."""
    if not log:
        return
    moves = state.setdefault("moves_log", [])
    for x in log:
        walked = re.findall(r"walked (?:forward |back )?about ([\d.,]+ ?c?m)", str(x.get("result", "")))
        moves.append((time.time(), x.get("step", ""), x.get("step", "") + (f" (walked about {walked[-1]})" if walked else "")))
    del moves[:-200]


def hold(text, who=None, their_words=None):
    """He chose to keep something in mind (a HOLD: line)."""
    if not WORKING_MEMORY:
        return
    text = (text or "").strip().strip('"').strip()
    if not text or re.fullmatch(r"(?i)\W*(none|no|nothing|n/?a)\W*", text):
        return
    wm = items()
    if any(_same(text, i["text"]) for i in wm):
        return
    wm.append({"text": text[:160], "t": time.time(), "who": who, "words": (their_words or "")[:200], "spot": _where()})
    del wm[:-WM_MAX]
    state["wm"] = wm
    print(f"🧷 (holding in mind: {text[:100]})")


def letgo(text):
    """He chose to let something go (a LETGO: line) - the item that shares the most words with it."""
    wm = items()
    if not wm or not text or re.fullmatch(r"(?i)\W*(none|no|nothing|n/?a)\W*", text.strip()):
        return
    best = max(wm, key=lambda i: _overlap(text, i["text"]))
    if _overlap(text, best["text"]) == 0 and len(wm) > 1:
        return
    wm.remove(best)
    state["wm"] = wm
    print(f"🧷 (let go: {best['text'][:100]})")


def _words(t):
    return {w for w in re.findall(r"[a-z']+", t.lower()) if len(w) > 2 and w not in ("the", "and", "you", "until", "this")}


def _overlap(a, b):
    return len(_words(a) & _words(b))


def _same(a, b):
    wa, wb = _words(a), _words(b)
    return bool(wa) and len(wa & wb) >= 0.7 * min(len(wa), len(wb))


def words(now=None):
    """What he is shown: each open item with who asked, their words, how long ago - and, right beside it, what his body
    has done since and how far he is from where he was then. Empty when nothing is open."""
    if not WORKING_MEMORY:
        return ""
    now = now or time.time()
    wm = items()
    if not wm:
        return ""
    here = _where()
    lines = []
    for i in wm:
        line = f"- ({_ago(now - i['t'])}) {i['text']}"
        if i.get("words"):
            line += f' – {i.get("who") or "they"} said: "{i["words"].strip().rstrip(".")}"'
        since = [m for m in state.get("moves_log", []) if m[0] >= i["t"]]
        walked = [m for m in since if re.search(MOVE_WORDS, m[1])]
        if since:
            keep = walked + [m for m in since if m not in walked][-3:]
            keep.sort(key=lambda m: m[0])
            rest = len(since) - len(keep)
            line += ". Since then your body: " + "; ".join(m[2] for m in keep) + (
                f"; and {rest} small moves on the spot" if rest > 0 else "")
        else:
            line += ". Since then your body hasn't moved."
        if i.get("spot") and here:
            d = math.hypot(here[0] - i["spot"][0], here[1] - i["spot"][1])
            line += (" You are still at about the same spot as then." if d < 0.4 else
                     f" You are now about {d:.1f} m from where you were then.")
        lines.append(line)
    return ("What you are holding in mind right now (things you agreed to or promised - you chose to keep these; they "
            "stay until you let them go):\n"
            + "\n".join(lines)
            + "\n(If one of these is done or no longer wanted, you can write a line LETGO: <a few words of it>.)\n")


def night_flush():
    """At night: what is still open goes into the diary, then the list is emptied. Returns the diary lines."""
    wm = items()
    state["wm"] = []
    state["moves_log"] = []
    return [f"Still open when I went to sleep: {i['text']}" for i in wm]
