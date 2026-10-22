#!/bin/bash
# Overnight run: 3 episodes x minutes 2-10 per show. Keeps the PC awake until done.
# Tonight's working demo is saved in runs/v1/ (restore by copying it back if this fails).
cd "$(dirname "$0")/.."
export HF_HUB_OFFLINE=1 VIBE_THREADS=6
VIBE=.venv/Scripts/vibe.exe
log() { echo "$(date +%H:%M:%S) $*"; }

# Block system sleep for as long as this script runs (no settings changed).
.venv/Scripts/python.exe -c "
import ctypes, time
ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
while True: time.sleep(60)" &
AWAKE=$!
trap 'kill $AWAKE 2>/dev/null' EXIT

run() { log "STEP $1 start"; $VIBE "$@" > runs/ov_$1.log 2> runs/ov_$1.err || { log "STEP $1 FAILED"; tail -5 runs/ov_$1.err; exit 1; }; log "STEP $1 done"; }

run segments
log "STEP embed+transcribe start"
$VIBE embed --model gemma > runs/ov_embed.log 2> runs/ov_embed.err & E=$!
$VIBE transcribe > runs/ov_transcribe.log 2> runs/ov_transcribe.err & W=$!
wait $E; e=$?; wait $W; w=$?
[ $e -ne 0 ] && { log "STEP embed FAILED"; tail -5 runs/ov_embed.err; exit 1; }
[ $w -ne 0 ] && { log "STEP transcribe FAILED"; tail -5 runs/ov_transcribe.err; exit 1; }
log "STEP embed+transcribe done"
run acoustic
run textemb
run evaluate
run demo

# Restart the local server on the new index.
taskkill //F //PID "$(cat runs/serve.pid | tr -d '\r\n ')" > /dev/null 2>&1
nohup $VIBE serve > runs/serve.log 2> runs/serve.err &
echo $! > runs/serve.pid
log "PIPELINE DONE"
