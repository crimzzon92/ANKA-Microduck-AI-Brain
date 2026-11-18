#!/bin/bash
# Anka suite – double-click (or run with a suite name). Runs the measuring scenarios one after another in the 2D body
# simulator, then scores them (test_logs/scores.csv). Uses the real cloud brain: each run costs about $0.10 and takes
# ~7 minutes (5-6 min day + the night). Leave the Mac alone while it runs; Ctrl+C stops after the current run.
#
#   "Anka suite.command"            = baseline   (alone, cup, sock, shout – 3 runs each, ≈ 12 runs, ~1.5 h, ≈ $1.30)
#   "Anka suite.command" feelings   = experiment 1: the same with his feelings held still (alone + shout, 6 runs)
#   "Anka suite.command" lonely     = experiment 2: alone with loneliness held HIGH (3 runs) and LOW (3 runs)
#   "Anka suite.command" twodays    = learning: the cup task on day 1, a night, the cup task again on day 2 (life mode)
#   "Anka suite.command" nextday    = one more day of the same life (cup task, life mode, memory kept) – run after twodays
#   "Anka suite.command" transfer   = TRANSFER TEST: cup (day 1) → night → the sock up on the sofa (day 2), vs the sofa task
#                                     in a fresh life (control) – ×3 (9 runs, ~65 min, ≈ $1.20)
#   "Anka suite.command" wise       = ASK THE WISER BRAIN WHEN STUCK: the ball in the corner, ×3 with / ×3 without (--no-wise), one day each (~42 min, ≈ $0.90)
#   "Anka suite.command" balltransfer = TRANSFER TEST 2: ball stuck in a corner (day 1) → ball against another wall (day 2):
#                                     WITH night ideas / WITHOUT ideas (--no-ideas) / fresh life (control) – ×3 (15 runs, ~1 h 50, ≈ $2)
#   "Anka suite.command" expect     = B1: the surprise scenario ×3 with expectations + ×3 without (--no-expect)
#   "Anka suite.command" echo       = shout ×3 with feelings that outlast the event + shout ×3 without (--no-echo)
#   "Anka suite.command" talk       = alone ×3 + cup ×3 (~42 min, ≈ $0.60) – how much he talks alone AND with Alex
#   "Anka suite.command" urge       = INNER URGE: alone ×3 + shout ×3 with the URGE line, the same ×3 + ×3 without (--no-urge)
#                                     (12 runs, ~85 min) – does a lonely Anka seek company, does he stay careful after a shout?
#   "Anka suite.command" moodlife   = FEELINGS COLOUR MEMORY in LIFE MODE (memories kept): a fresh life, day 1 alone -> night ->
#                                     day 2 cup task; with and without (--no-mood-memory), ×2 (8 runs, ~1 h)
#   "Anka suite.command" familiar   = FAMILIARITY: 3 days alone in life mode with "how well you know what is here", then
#                                     the same 3 days without (--no-familiarity), two lives each (12 runs, ~1.5 h, ≈ $1.20)
#   "Anka suite.command" lessons    = LESSONS AS EXPERIENCES: 3 days alone in life mode with the lesson fix, then without
#                                     (--no-lesson-fix), two lives each (12 runs, ~1.5 h, ≈ $1.20)
#   "Anka suite.command" assoc      = ASSOCIATIONS (gemma3:1b writes memory search words): alone ×2 + cup ×2 WITH only - compared with
#                                     the earlier runs without (11-18 17:10-18:23) (4 runs, ~30 min, ≈ $0.40)
#   "Anka suite.command" restless   = RESTLESSNESS: 3 days alone in life mode, two lives, WITH only - compared with
#                                     the lesson-fix runs of suite "lessons" (11-18 15:11-16:31) (6 runs, ~45 min, ≈ $0.60)
#   "Anka suite.command" mood       = FEELINGS COLOUR MEMORY: alone ×3 + shout ×3 with, the same ×3 + ×3 without (--no-mood-memory)
#   "Anka suite.command" localurge  = FEELING LAYER: alone ×3 + shout ×3 with the local feeling model, the same ×3 + ×3 without
#   "Anka suite.command" quick      = one run of each scenario (4 runs) – to check that everything works
cd "$(dirname "$0")/.." || exit 1
PY="$HOME/anka-env/bin/python"
SUITE="${1:-baseline}"
case "$SUITE" in
    baseline) RUNS=("alone" "cup" "sock" "shout" "alone" "cup" "sock" "shout" "alone" "cup" "sock" "shout") ;;
    feelings) RUNS=("alone --frozen-feelings" "shout --frozen-feelings" "alone --frozen-feelings"
                    "shout --frozen-feelings" "alone --frozen-feelings" "shout --frozen-feelings") ;;
    lonely)   RUNS=("alone --feelings loneliness=0.9" "alone --feelings loneliness=0.1"
                    "alone --feelings loneliness=0.9" "alone --feelings loneliness=0.1"
                    "alone --feelings loneliness=0.9" "alone --feelings loneliness=0.1") ;;
    twodays)  RUNS=("cup --life --newlife" "cup --life") ;;
    nextday)  RUNS=("cup --life") ;;
    quick)    RUNS=("alone" "cup" "sock" "shout") ;;
    talk)     RUNS=("alone" "cup" "alone" "cup" "alone" "cup") ;;
    transfer) RUNS=("cup --life --newlife" "high --life" "high --life --newlife"
                    "cup --life --newlife" "high --life" "high --life --newlife"
                    "cup --life --newlife" "high --life" "high --life --newlife") ;;
    wise)     RUNS=("ballcorner --life --newlife" "ballcorner --life --newlife --no-wise"
                    "ballcorner --life --newlife" "ballcorner --life --newlife --no-wise"
                    "ballcorner --life --newlife" "ballcorner --life --newlife --no-wise") ;;
    balltransfer) RUNS=("ballcorner --life --newlife" "ballwall --life" "ballcorner --life --newlife --no-ideas" "ballwall --life --no-ideas" "ballwall --life --newlife"
                    "ballcorner --life --newlife" "ballwall --life" "ballcorner --life --newlife --no-ideas" "ballwall --life --no-ideas" "ballwall --life --newlife"
                    "ballcorner --life --newlife" "ballwall --life" "ballcorner --life --newlife --no-ideas" "ballwall --life --no-ideas" "ballwall --life --newlife") ;;
    expect)   RUNS=("surprise" "surprise --no-expect" "surprise" "surprise --no-expect" "surprise" "surprise --no-expect") ;;
    urge)     RUNS=("alone --urge same" "alone --no-urge" "shout --urge same" "shout --no-urge" "alone --urge same" "alone --no-urge"
                    "shout --urge same" "shout --no-urge" "alone --urge same" "alone --no-urge" "shout --urge same" "shout --no-urge") ;;
    moodlife) RUNS=("alone --life --newlife" "cup --life" "alone --life --newlife --no-mood-memory" "cup --life --no-mood-memory"
                    "alone --life --newlife" "cup --life" "alone --life --newlife --no-mood-memory" "cup --life --no-mood-memory") ;;
    familiar) RUNS=("alone --life --newlife" "alone --life" "alone --life"
                    "alone --life --newlife --no-familiarity" "alone --life --no-familiarity" "alone --life --no-familiarity"
                    "alone --life --newlife" "alone --life" "alone --life"
                    "alone --life --newlife --no-familiarity" "alone --life --no-familiarity" "alone --life --no-familiarity") ;;
    lessons)  RUNS=("alone --life --newlife" "alone --life" "alone --life"
                    "alone --life --newlife --no-lesson-fix" "alone --life --no-lesson-fix" "alone --life --no-lesson-fix"
                    "alone --life --newlife" "alone --life" "alone --life"
                    "alone --life --newlife --no-lesson-fix" "alone --life --no-lesson-fix" "alone --life --no-lesson-fix") ;;
    assoc)    RUNS=("alone" "cup" "alone" "cup") ;;   # (v4, 2026-11-18: only WITH - compared with the earlier runs without)
    restless) RUNS=("alone --life --newlife" "alone --life" "alone --life"
                    "alone --life --newlife" "alone --life" "alone --life") ;;   # (WITH only - compare with suite "lessons")
    mood)     RUNS=("alone" "alone --no-mood-memory" "shout" "shout --no-mood-memory" "alone" "alone --no-mood-memory"
                    "shout" "shout --no-mood-memory" "alone" "alone --no-mood-memory" "shout" "shout --no-mood-memory") ;;
    localurge) RUNS=("alone --urge local" "alone --no-urge" "shout --urge local" "shout --no-urge" "alone --urge local" "alone --no-urge"
                    "shout --urge local" "shout --no-urge" "alone --urge local" "alone --no-urge" "shout --urge local" "shout --no-urge") ;;
    echo)     RUNS=("shout" "shout --no-echo" "shout" "shout --no-echo" "shout" "shout --no-echo") ;;
    *) echo "Unknown suite '$SUITE' (baseline, feelings, lonely, twodays, nextday, quick, talk, echo, urge, localurge, mood, moodlife, expect, transfer, balltransfer, wise, familiar, lessons, assoc, restless)"; read -r -p "Press Enter..."; exit 1 ;;
esac
if [ ! -x "$PY" ]; then echo "❌ Can't find $PY"; read -r -p "Press Enter..."; exit 1; fi
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then open -a Ollama; sleep 8; fi   # (memory search needs it)

STARTED=$(date +%Y-%m-%d_%H%M)
echo "📈 Suite '$SUITE': ${#RUNS[@]} runs, about $(( ${#RUNS[@]} * 7 )) minutes. Started $(date +%H:%M)."
i=0
for RUN in "${RUNS[@]}"; do
    i=$((i + 1))
    set -- $RUN
    SCEN="$1"; shift
    echo; echo "================ run $i of ${#RUNS[@]}: $SCEN $* ($(date +%H:%M)) ================"
    "$PY" run_anka.py --simulate --body --scenario "$SCEN" "$@" || echo "⚠️  run $i ended with an error – going on"
    sleep 3
done

echo; echo "📈 Scoring..."
"$PY" tools/score_run.py >/dev/null
SINCE_ARGS=""; [ "$SUITE" = "echo" ] && SINCE_ARGS="shout --since $STARTED"
[ "$SUITE" = "expect" ] && SINCE_ARGS="surprise --since $STARTED"
[ "$SUITE" = "wise" ] && SINCE_ARGS="ballcorner --since $STARTED"
if [ "$SUITE" = "balltransfer" ]; then
    "$PY" tools/score_run.py --transfer "$STARTED" ballwall | tee "test_logs/compare_$(date +%Y-%m-%d_%H%M)_$SUITE.txt"
elif [ "$SUITE" = "transfer" ]; then
    "$PY" tools/score_run.py --transfer "$STARTED" | tee "test_logs/compare_$(date +%Y-%m-%d_%H%M)_$SUITE.txt"
else
    "$PY" tools/score_run.py --compare $SINCE_ARGS | tee "test_logs/compare_$(date +%Y-%m-%d_%H%M)_$SUITE.txt"
fi
echo; echo "✅ Suite '$SUITE' done $(date +%H:%M). Scores: test_logs/scores.csv"
read -r -p "Press Enter to close this window..."
