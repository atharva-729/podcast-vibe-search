#!/bin/bash
# Wait for embed + whisper, then run the rest of the pipeline.
cd "$(dirname "$0")/.."
while tasklist //FI "PID eq 3792" | grep -q 3792 || tasklist //FI "PID eq 12200" | grep -q 12200; do sleep 20; done
export HF_HUB_OFFLINE=1
for step in textemb evaluate demo; do
  echo "STEP $step start $(date +%H:%M:%S)"
  .venv/Scripts/vibe.exe $step > runs/step_$step.log 2> runs/step_$step.err || { echo "STEP $step FAILED"; tail -5 runs/step_$step.err; exit 1; }
  echo "STEP $step done $(date +%H:%M:%S)"
done
echo "PIPELINE DONE"
