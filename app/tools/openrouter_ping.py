"""Checks the OpenRouter connection before a test (2026-11-20): your key's limits, and one tiny question with a
picture to the model Anka would use. Costs nothing on a free model (it counts as 1 of the day's free requests).

    ~/anka-env/bin/python tools/openrouter_ping.py      (or double-click tools/"OpenRouter ping.command")"""
import base64
import json
import os
import sys
import time
import urllib.request

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP)
_arg = " ".join(sys.argv[1:])
sys.argv = [sys.argv[0], "--qwen27b" if "qwen" in _arg else "--gemma4" if "gemma4" in _arg else "--gemma27b" if "gemma" in _arg else "--openrouter"]   # ("qwen" = test Qwen3.8 27B)
import settings  # noqa: E402

key = settings.CLOUD_KEY
if not key:
    sys.exit("❌ No key: put it in app/openrouter.key (one line).")
print(f"🔑 key {key[:10]}...  model {settings.OPENROUTER_MODEL}")
try:
    req = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": "Bearer " + key})
    info = json.load(urllib.request.urlopen(req, timeout=20)).get("data", {})
    print(f"📊 free tier (never bought credits): {info.get('is_free_tier')} · credit limit: {info.get('limit')} · "
          f"used: {info.get('usage')}")
    print("   (free models: 20 requests a minute; 50 a day without credits, 1,000 a day once $10 has been bought -"
          " an Anka test day uses 50-150)")
except Exception as error:
    print(f"⚠️  couldn't read the key's limits: {error}")

picture = None
for name in ("room_map.png", os.path.join("docs", "anka-avatar.png")):
    p = os.path.join(APP, name)
    if os.path.exists(p):
        picture = base64.b64encode(open(p, "rb").read()).decode()
        break
content = [{"type": "text", "text": "You are a small robot duck. In one short sentence: what do you see in this picture?"}]
if picture:
    content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + picture}})
variants = [("thinking low, room 2000", {"reasoning": {"effort": "low", "exclude": True}, "max_tokens": 2000}),
            ("thinking OFF", {"reasoning": {"enabled": False}, "max_tokens": 600}),
            ("no setting", {"max_tokens": 2000})]
for label, extra in variants:
    body = {"model": settings.OPENROUTER_MODEL, "messages": [{"role": "user", "content": content}], **extra}
    req = urllib.request.Request(settings.CLOUD_URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    t = time.time()
    try:
        answer = json.load(urllib.request.urlopen(req, timeout=120))
        ch = answer["choices"][0]
        msg = ch.get("message", {})
        reasoning = msg.get("reasoning") or ""
        print(f"\n▶ {label}: {time.time() - t:.1f} s · finish: {ch.get('finish_reason')} · tokens: {answer.get('usage')}")
        print(f"   answer: {msg.get('content')!r}")
        if reasoning:
            print(f"   (its quiet thinking, {len(reasoning)} chars): {reasoning[:200]!r}")
    except urllib.error.HTTPError as error:
        print(f"\n▶ {label}: ❌ {error.code}: {error.read().decode(errors='ignore')[:300]}")
    except Exception as error:
        print(f"\n▶ {label}: ❌ {error}")
