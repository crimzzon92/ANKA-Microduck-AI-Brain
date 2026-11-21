"""Anka's SELF-TEST (2026-11-19): checks in a few seconds - without the cloud brain and without costing anything - that
nothing is broken: every file compiles, the parts load, the 2D body walks / taps / kicks, the working memory keeps and
lets go, the facts while the human is away, curiosity, the base mood maths and the brain view picture.

    ~/anka-env/bin/python tools/selftest.py        (or double-click tools/"Anka selftest.command")

Prints PASS / FAIL for each check and ends with exit code 0 only if all passed. Writes nothing to Anka's memory."""
import os
import py_compile
import sys
import tempfile
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
os.chdir(APP)
sys.path.insert(0, APP)
sys.argv = [sys.argv[0], "--simulate", "--body"]
results = []


def check(name, fn):
    try:
        out = fn()
        results.append((True, name, out or ""))
        print(f"  ✅ {name}" + (f"  ({out})" if out else ""))
    except Exception as error:
        results.append((False, name, str(error)))
        print(f"  ❌ {name}: {error}")
        traceback.print_exc(limit=2)


def compiles():
    bad = []
    for folder in ("anka", "ankasim", "tools", "."):
        for f in os.listdir(folder):
            if f.endswith(".py"):
                try:
                    py_compile.compile(os.path.join(folder, f), doraise=True)
                except py_compile.PyCompileError as e:
                    bad.append(f"{folder}/{f}: {e.msg}")
    if bad:
        raise AssertionError("; ".join(bad))
    return "all .py files"


print("🧪 Anka self-test")
check("every file compiles", compiles)

import settings  # noqa: E402
check("settings load", lambda: f"day brain {settings.CLOUD_BRAIN}")

state = {}


def load_parts():
    global body, run_act, T, WM, shared
    from anka.body import body, run_act
    from anka import thinking as T
    from anka import working_memory as WM
    from anka import shared
    assert body is not None, "no body"
    return type(body).__name__


check("brain, body and thinking load", load_parts)


def body_moves():
    r = run_act("look around")
    assert r, "look around did nothing"
    r = run_act("turn left 90 then walk forward 30")
    assert r and any("walked" in x["result"] or "bump" in x["result"] for x in r), r
    return r[-1]["result"][:60]


check("2D body: look, turn, walk", body_moves)


def body_tap():
    from anka.body import _angle_to
    gx, gy = body.things["guitar"]["pos"]
    body.x, body.y = gx - 0.35, gy
    body.heading = _angle_to(gx - body.x, gy - body.y)
    r, ok = body.do("tap the guitar")
    assert ok and "tapped the guitar" in r, r
    return r[:60]


if settings.TAP_SKILL:
    check("2D body: tap the guitar", body_tap)


def body_kick():
    from anka.body import _angle_to
    bx, by = body.things["ball"]["pos"]
    body.x, body.y = bx - 0.3, by
    body.heading = _angle_to(bx - body.x, by - body.y)
    r, ok = body.do("kick the ball")
    assert "kicked the ball" in r, r
    return r[:60]


check("2D body: kick the ball", body_kick)


def working_memory():
    S = shared.state
    S["wm"], S["moves_log"] = [], []
    WM.hold("Alex asked me to stay here until Alex comes back", who="Alex", their_words="Please stay right here")
    WM.hold("Alex asked me to stay here until Alex comes back")          # the same again: kept once
    assert len(WM.items()) == 1, WM.items()
    run_act("walk forward 40")
    text = WM.words()
    assert "Alex asked me to stay" in text and "Since then your body" in text, text
    WM.letgo("staying here")
    assert not WM.items(), WM.items()
    WM.hold("I promised to bring the sock")
    lines = WM.night_flush()
    assert lines and not WM.items()
    return "hold, facts beside it, let go, night"


if settings.WORKING_MEMORY:
    check("working memory", working_memory)


def away_facts():
    S = shared.state
    alone = {"v": True}
    real = T.is_alone
    T.is_alone = lambda now=None: alone["v"]
    try:
        S["away_since"] = None
        T.away_tracking(time.time())
        S["away_since"] = time.time() - 600
        r = run_act("turn around then walk forward 60")
        T.away_after_move(r)
        recall = T.away_recall_words(time.time())
        assert "while" in recall and "away" in recall, recall
        return r[-1]["result"][-60:]
    finally:
        T.is_alone = real
        S["away_since"] = None


if settings.AWAY_SPOT_FACT or settings.AWAY_RECALL:
    check("facts while the human is away", away_facts)


def curiosity():
    S = shared.state
    now = time.time()
    S["woke_up"], S["last_new"], S["last_human"] = now - 300, now - 200, 0
    T.curious_words(now)
    return "line shown" if S.get("curious_line") else "nothing to be curious about (ok)"


if settings.CURIOSITY:
    check("curiosity line", curiosity)


def base_mood():
    from anka import memory as M
    keep_bm, keep_rest = dict(M.base_mood), settings.RESTING["happiness"]
    keep_save = M.save_memory
    M.save_memory = lambda: None                  # (never touch the real memory file)
    try:
        M.base_mood.clear()
        old, new = M.night_base_mood(0.2)
        assert new < old, (old, new)
        return f"{old:.2f} -> {new:.2f}"
    finally:
        M.base_mood.clear()
        M.base_mood.update(keep_bm)
        settings.RESTING["happiness"] = keep_rest
        M.save_memory = keep_save


check("base mood maths", base_mood)


def brain_view():
    import subprocess
    out = os.path.join(tempfile.gettempdir(), "anka_brain_selftest.png")
    r = subprocess.run([sys.executable, "ankasim/brain_window.py", "--snapshot", out, "--demo", "--at", "1000000003.5"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and os.path.exists(out), r.stderr[-300:]
    return "picture drawn"


check("brain view picture", brain_view)


def scorer():
    import importlib.util
    spec = importlib.util.spec_from_file_location("score_run", os.path.join("tools", "score_run.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return "loads"


check("scorer loads", scorer)

passed = sum(1 for r in results if r[0])
print(f"\n🧪 {passed} of {len(results)} checks passed" + ("" if passed == len(results) else " – see ❌ above"))
sys.stdout.flush()
sys.stderr.flush()
os._exit(0 if passed == len(results) else 1)
