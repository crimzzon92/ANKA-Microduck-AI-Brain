"""A0 – which small local model is best as Anka's FEELING LAYER? (2026-11-15)

The feeling layer is a small model that can NOT see the room. It only gets his feelings (and the big feelings that
still linger) and writes what he wants right now, in a few words. This test feeds the same saved feeling moments
from old test runs to a few small models and writes a report, so we can pick one before building anything.

Run:  double-click "Urge models test.command" (in this folder), or:  python tools/urge_models_test.py
It needs Ollama. Missing models are downloaded first (0.5–1.5 GB each). Takes about 10–15 minutes.
The report is written to test_logs/urge_models_<date>.md
"""
import glob
import json
import os
import random
import subprocess
import time
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # the app folder
LOGS = os.path.join(HERE, "test_logs")
OLLAMA = "http://localhost:11434"
MODELS = ["qwen3.5:0.8b", "gemma3:1b", "llama3.2:1b", "qwen3.5:2b"]    # all 2 B or smaller
MOMENTS = 24

NAMES = {"curiosity": "curious", "boredom": "bored", "loneliness": "lonely", "happiness": "happy",
         "affection": "loving", "nervousness": "nervous", "playfulness": "playful"}

SYSTEM = ("You are the feelings inside a small duck robot called Anka. You cannot see or hear anything - you only "
          "feel. Say what these feelings make Anka WANT right now, in one short sentence in first person "
          "(at most 10 words), like an animal's urge. Only the wish, nothing else.")


def level(v):
    return "a little" if v < 0.35 else "quite" if v < 0.7 else "very"


def moment_text(m):
    """What the feeling layer is told: the feelings in words, lingering feelings, and whether someone is there."""
    f = m["feel"]
    strong = sorted(f.items(), key=lambda kv: -abs(kv[1] - (0.0 if kv[0] in ("boredom", "nervousness") else 0.4)))
    words = ", ".join(f"{level(v)} {NAMES[k]}" for k, v in strong if v >= 0.2)
    text = f"Anka feels: {words or 'calm'}."
    if m.get("echo"):
        text += "\n" + m["echo"].split(":\n", 1)[-1].strip()
    text += "\nSomeone he knows is with him." if m.get("human_here") else "\nHe is alone."
    if m.get("last_urges"):
        text += "\nWhat he wanted a moment ago: " + "; ".join(m["last_urges"])
    return text + "\nWhat does Anka want right now?"


def collect_moments():
    """Feeling moments from saved test runs - spread over lonely, scared, bored, playful, happy and mixed ones."""
    found = []
    for path in sorted(glob.glob(os.path.join(LOGS, "trace_*.jsonl"))):
        try:
            rows = [json.loads(line) for line in open(path, encoding="utf-8")]
        except Exception:
            continue
        for r in rows:
            f = r.get("feel_before")
            if r.get("kind") != "thought" or not isinstance(f, dict) or len(f) < 7:
                continue
            found.append({"feel": {k: float(f[k]) for k in NAMES if k in f}, "echo": r.get("echo"),
                          "human_here": bool(r.get("human_here")), "from": os.path.basename(path)})
    random.seed(7)
    random.shuffle(found)
    buckets = {}
    for m in found:
        f = m["feel"]
        key = max(("loneliness", "nervousness", "boredom", "playfulness", "happiness", "curiosity"),
                  key=lambda k: f.get(k, 0))
        if m.get("echo"):
            key = "lingering"
        buckets.setdefault(key, []).append(m)
    picked, i = [], 0
    while len(picked) < MOMENTS and any(buckets.values()):
        for key in list(buckets):
            if buckets[key] and len(picked) < MOMENTS:
                picked.append(buckets[key].pop())
        i += 1
    return picked


def ollama(path, body=None, timeout=600):
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def have(model):
    try:
        names = [m["name"] for m in ollama("/api/tags")["models"]]
    except Exception:
        return False
    return any(n == model or n == model + ":latest" for n in names)


def ask(model, text):
    t = time.time()
    out = ollama("/api/chat", {"model": model, "stream": False, "think": False, "keep_alive": "5m",
                               "options": {"num_ctx": 1024, "num_predict": 30, "temperature": 0.8},
                               "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]},
                 timeout=120)
    answer = " ".join((out.get("message") or {}).get("content", "").split())
    return answer, time.time() - t


def memory_of(model):
    """How much memory Ollama uses for the loaded model (from 'ollama ps')."""
    try:
        for m in ollama("/api/ps").get("models", []):
            if m.get("name", "").startswith(model):
                return m.get("size", 0) / 1e9
    except Exception:
        pass
    return None


def main():
    try:
        ollama("/api/tags")
    except Exception:
        print("❌ Ollama isn't running. Start it (open the Ollama app) and try again.")
        return
    moments = collect_moments()
    if not moments:
        print("❌ No saved test runs with feelings found in test_logs.")
        return
    print(f"🧪 {len(moments)} feeling moments from old test runs, {len(MODELS)} models.\n")
    results = {}
    for model in MODELS:
        if not have(model):
            print(f"⬇️  Downloading {model} (once) ...")
            if subprocess.run(["ollama", "pull", model]).returncode != 0:
                print(f"   ❌ could not download {model} – skipped")
                continue
        print(f"🧠 {model}: loading ...")
        try:
            _, load_s = ask(model, "Anka feels: quite curious.\nHe is alone.\nWhat does Anka want right now?")
        except Exception as error:
            print(f"   ❌ {model} didn't answer ({error}) – skipped")
            continue
        answers, secs = [], []
        for i, m in enumerate(moments, 1):
            try:
                a, s = ask(model, moment_text(m))
            except Exception as error:
                a, s = f"(error: {error})", 0.0
            answers.append(a)
            secs.append(s)
            print(f"   {i:2d}. {a[:70]}   ({s:.1f}s)")
        results[model] = {"answers": answers, "secs": secs, "load": load_s, "memory": memory_of(model)}
        try:
            ollama("/api/generate", {"model": model, "keep_alive": 0})     # unload before the next one
        except Exception:
            pass
        print()

    stamp = time.strftime("%Y-%m-%d_%H%M")
    path = os.path.join(LOGS, f"urge_models_{stamp}.md")
    with open(path, "w", encoding="utf-8") as out:
        out.write(f"# Feeling layer – small models compared ({stamp})\n\n")
        out.write("| model | memory (GB) | first answer incl. loading (s) | per urge, average (s) | slowest (s) |\n|---|---|---|---|---|\n")
        for model, r in results.items():
            mem = f"{r['memory']:.2f}" if r["memory"] else "?"
            out.write(f"| {model} | {mem} | {r['load']:.1f} | {sum(r['secs']) / len(r['secs']):.2f} | {max(r['secs']):.1f} |\n")
        out.write("\n## The moments and the urges\n")
        for i, m in enumerate(moments):
            out.write(f"\n### {i + 1}. ({m['from']})\n```\n{moment_text(m)}\n```\n")
            for model, r in results.items():
                out.write(f"- **{model}** ({r['secs'][i]:.1f}s): {r['answers'][i]}\n")
    print(f"📄 Report: {path}")


if __name__ == "__main__":
    main()
