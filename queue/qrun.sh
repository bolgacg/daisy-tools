#!/bin/bash
# Sequential job queue for the box. Jobs are bash scripts in ~/queue/pending, run in name order, one at a time.
# Survives reboots (systemd restarts it; a job found in running/ is retried once). Never starts a job while
# another GPU user is alive. Logs: ~/queue/logs/<job>.log and ~/queue/logs/queue.log
Q=$HOME/queue; mkdir -p $Q/pending $Q/running $Q/done $Q/failed $Q/logs
log(){ echo "$(date +%F_%T) $*" >> $Q/logs/queue.log; }
for j in $(ls $Q/running 2>/dev/null); do mv $Q/running/$j $Q/pending/$j; log "REQUEUE $j (found running at start)"; done
log "queue runner started"
while true; do
  job=$(ls $Q/pending 2>/dev/null | sort | head -1)
  if [ -z "$job" ]; then sleep 20; continue; fi
  while pgrep -f "llama-server|mimir_official.py|run_logprobs.sh|run_all.sh|run_extra.sh" >/dev/null; do sleep 30; done
  mv $Q/pending/$job $Q/running/$job; log "START $job"
  if bash $Q/running/$job > $Q/logs/$job.log 2>&1; then mv $Q/running/$job $Q/done/$job; log "DONE $job"
  else mv $Q/running/$job $Q/failed/$job; log "FAIL $job (see logs/$job.log)"; fi
  sleep 5
done
