#!/bin/bash
# Anka self-test - checks in a few seconds (no cloud, free) that nothing is broken.
cd "$(dirname "$0")/.." || exit 1
PY="$HOME/anka-env/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" tools/selftest.py
read -r -p "Press Enter to close..."
