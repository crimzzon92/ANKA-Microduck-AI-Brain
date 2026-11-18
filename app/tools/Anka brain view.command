#!/bin/bash
# Anka brain view - double-click. A small local page (app/viz/index.html) that shows which parts of Anka are busy:
# Vision, Attention, Goals, Memory, Movement, Feelings, Hearing & speech. Start it before or after Anka - Anka runs the
# same with it closed. "Anka brain view (demo).command" opens it in DEMO mode (no Anka needed).
cd "$(dirname "$0")/.." || exit 1
PY="$HOME/anka-env/bin/python"; [ -x "$PY" ] || PY=python3
PORT=8765
if ! curl -s "http://127.0.0.1:$PORT/index.html" >/dev/null 2>&1; then
    "$PY" -m http.server "$PORT" --bind 127.0.0.1 --directory viz >/dev/null 2>&1 &
    SRV=$!
    sleep 1
fi
URL="http://127.0.0.1:$PORT/"; [ "$1" = "demo" ] && URL="$URL?demo"
if command -v open >/dev/null 2>&1; then open "$URL"; else xdg-open "$URL" >/dev/null 2>&1; fi
echo "🧠 Anka brain view: $URL"
read -r -p "Press Enter to stop the brain view..."
[ -n "$SRV" ] && kill "$SRV" 2>/dev/null
