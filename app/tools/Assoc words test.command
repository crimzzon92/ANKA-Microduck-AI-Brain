#!/bin/bash
# Double-click: which association words does gemma3:1b write? (needs Ollama)
cd "$(dirname "$0")/.." || exit 1
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then open -a Ollama; sleep 8; fi
"$HOME/anka-env/bin/python" tools/assoc_words_test.py
read -r -p "Press Enter to close this window..."
