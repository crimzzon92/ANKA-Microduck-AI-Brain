#!/bin/bash
# Checks the OpenRouter key and the Qwen3.8 27B model with a few tiny questions (costs almost nothing).
cd "$(dirname "$0")/.." || exit 1
PY="$HOME/anka-env/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" tools/openrouter_ping.py qwen
read -r -p "Press Enter to close..."
