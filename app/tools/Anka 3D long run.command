#!/bin/bash
# Anka 3D long run – double-click and leave the Mac alone. Runs a short 3D day several times in a row, so there are
# many kick tries to measure afterwards. Default: the "kick" day (only the ball, asked to kick it 4 times, ~6 min +
# the night, ~10 min with the start) × 5 = about 50 min.
# Each run is a fresh day (no life mode), with Pollen's MuJoCo simulator started and stopped for every run.
# Every kick approach is written to the thought log (kind "kick_approach" in test_logs/trace_*.jsonl).
#   ./"Anka 3D long run.command" 3         = only 3 runs
#   ./"Anka 3D long run.command" 3 all     = 3 runs of the whole "everything" day instead
# Ctrl+C stops it.
cd "$(dirname "$0")/.." || exit 1
N="${1:-5}"
SCEN="${2:-kick}"
echo "🦆 3D long run: $N runs of the '$SCEN' day. Started $(date +%H:%M)."
for i in $(seq 1 "$N"); do
    echo; echo "================ 3D run $i of $N ($(date +%H:%M)) ================"
    bash "Start everything.command" --scenario "$SCEN" --auto-close || echo "⚠️  run $i ended with an error – going on"
    sleep 5
done
echo; echo "✅ 3D long run done $(date +%H:%M). Logs: test_logs/"
read -r -p "Press Enter to close this window..."
