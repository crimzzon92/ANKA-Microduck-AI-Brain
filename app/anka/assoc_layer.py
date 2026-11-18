"""ASSOCIATIONS for the memory search (2026-11-18, memory item 4): a small local model (gemma3:1b in Ollama) reads what is
happening - what he sees, what just happened, his latest thought, his goal - and writes a few words this moment might
remind him of ("kick, wall, stuck, rolled away"). The memory search uses them as well as the moment itself, so memories
come up by association, not only by the same words.

It sees NO feelings (they already colour memory through the mood search) and writes only search words - never wishes or
choices (the urge layer of 2026-11-15 wrote wishes, blind to the room, and made him passive). It changes what he
REMEMBERS, never what he does. If Ollama or the model is missing, the search just works as before."""
import json
import re
import threading
import time
import urllib.request

from settings import ASSOC_MODEL

SYSTEM = ("You help a small robot duck remember things. You get what is happening to him right now. Write 4 to 8 short "
          "words or phrases this moment might REMIND him of - related things, actions and earlier happenings that are NOT "
          "already in the text (a ball by a wall -> kick, bounce, stuck, rolled away; a cup too high -> climb, table, "
          "can't reach, ask for help). Do not just repeat the words of the text. Only the words, separated by commas. "
          "No sentences, no feelings, no wishes, no advice.")
# (v2, 2026-11-18: v1 mostly repeated the moment's own words - "sofa, door, going, later, out" - which adds little to the
#  search, since the moment itself is already searched)

_lock = threading.Lock()
_moment = {"text": "", "search": None, "words": None, "busy": False, "done": threading.Event()}
_fails = [0]


def _ask(text):
    body = {"model": ASSOC_MODEL, "stream": False, "think": False, "keep_alive": "30m",
            "options": {"num_ctx": 1024, "num_predict": 40, "temperature": 0.3},
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text[-700:]}]}
    req = urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        out = json.loads(r.read().decode())
    return new_words(clean(((out.get("message") or {}).get("content") or "")), text)


def new_words(words, text):
    """Keeps only what is NOT already in the moment's own text (v3, 2026-11-18: gemma3:1b still repeated half of it -
    "blue, floor, window, sock, near" - and the moment itself is searched anyway). None if fewer than 2 are left."""
    if not words:
        return None
    seen = set(re.findall(r"[a-z']+", text.lower()))
    stem = lambda w: w[:-1] if w.endswith("s") and len(w) > 3 else w
    seen |= {stem(w) for w in seen}
    keep = [p for p in words.split(", ") if not all(w in seen or stem(w) in seen for w in p.split())]
    # v4 (suite "assoc" 11-18: "near, walk, 2m, 80cm, turn, explore" brought up unrelated memories): no numbers or
    # measures, no plain body/place words that fit everything
    keep = [p for p in keep if not re.search(r"\d", p)
            and not all(w in GENERIC or stem(w) in GENERIC for w in p.split())]
    return ", ".join(keep) if len(keep) >= 2 else None


GENERIC = {"near", "far", "close", "walk", "walking", "turn", "turning", "look", "looking", "see", "seeing", "explore",
           "exploring", "move", "moving", "go", "going", "come", "left", "right", "ahead", "behind", "front", "back",
           "here", "there", "room", "floor", "thing", "something", "cm", "m", "meter", "meters", "distance", "way",
           "step", "steps", "now", "today", "time", "around", "side", "up", "down", "the", "a", "an"}


def clean(answer):
    """'Kick, the wall!, rolled away yesterday.' -> 'kick, the wall, rolled away yesterday' (None if nothing usable)."""
    parts = []
    for p in re.split(r"[,;\n]", answer or ""):
        p = re.sub(r"[^A-Za-z0-9' -]", "", p).strip(" -'").lower()
        if p and len(p.split()) <= 4 and p not in parts:
            parts.append(p)
    return ", ".join(parts[:10]) if len(parts) >= 2 else None


def _work(text):
    try:
        words = _ask(text)
        _fails[0] = 0
    except Exception:
        words = None
        _fails[0] += 1
    with _lock:
        if _moment["text"] == text:
            _moment["words"] = words
        _moment["busy"] = False
    _moment["done"].set()


def set_moment(text, search):
    """A new thought is coming: start writing association words for this moment (in the background)."""
    if not text or _fails[0] >= 3:
        return
    with _lock:
        if text == _moment["text"]:
            _moment["search"] = search
            return
        _moment.update(text=text, search=search, words=None, busy=True)
        _moment["done"] = threading.Event()
    threading.Thread(target=_work, args=(text,), daemon=True).start()


def words_for(search, wait=1.5):
    """The association words for this search (only the thought's own search), waiting a little if they are on the way."""
    with _lock:
        if _moment["search"] != search:
            return None
        done = _moment["done"]
    done.wait(wait)
    with _lock:
        return _moment["words"] if _moment["search"] == search else None
