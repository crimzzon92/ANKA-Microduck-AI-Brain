"""Quick look (2026-11-18): which association words does gemma3:1b write for a few moments? Needs Ollama running.
    ~/anka-env/bin/python tools/assoc_words_test.py"""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from anka.assoc_layer import _ask

MOMENTS = [
    "You see: a red ball about 30 cm ahead, by the wall. Your last thought: I kicked it but it didn't roll.",
    "Alex just said: I'm going out for a while. See you later! You see: the sofa, the door.",
    "You see: a guitar by the bookshelf. Your last thought: I wonder what sound the strings make.",
    "You see: a blue sock on the floor near the window. Your goal: bring Alex the sock.",
    "You see: the table with a cup on it, too high. Your last thought: I can't reach the cup.",
    "Nothing happened for a while. You see: the bookshelf, the window. Your last thought: the room is so quiet.",
]
for m in MOMENTS:
    t0 = time.time()
    try:
        words = _ask(m)
    except Exception as error:
        words = f"(error: {error})"
    print(f"{time.time() - t0:4.1f}s  {m[:70]}...\n       -> {words}\n")
