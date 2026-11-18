#!/bin/bash
# Anka brain window - double-click. Its own window (no web browser) showing which parts of Anka are busy, with light
# running through the neurons in waves. Normally you open it with the BRAIN VIEW button (or B) in the simulator.
# Add "demo" (or use "Anka brain window (demo).command") for demo mode. In the window: D = demo on/off, Q = close.
cd "$(dirname "$0")/.." || exit 1
PY="$HOME/anka-env/bin/python"; [ -x "$PY" ] || PY=python3
if [ "$1" = "demo" ]; then "$PY" ankasim/brain_window.py --demo; else "$PY" ankasim/brain_window.py; fi
