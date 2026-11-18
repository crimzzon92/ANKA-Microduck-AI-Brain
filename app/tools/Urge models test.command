#!/bin/bash
# A0: compare small local models as Anka's feeling layer (see urge_models_test.py). About 10-15 minutes.
cd "$(dirname "$0")/.." || exit 1
PY="$HOME/anka-env/bin/python"
[ -x "$PY" ] || PY=python3
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    open -a Ollama
    for i in $(seq 1 20); do curl -s http://localhost:11434/api/tags >/dev/null 2>&1 && break; sleep 0.5; done
fi
"$PY" tools/urge_models_test.py
read -r -p "Press Enter to close..."
