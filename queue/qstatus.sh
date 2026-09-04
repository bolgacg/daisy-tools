#!/bin/bash
Q=$HOME/queue
echo "pending: $(ls $Q/pending | tr '\n' ' ')"; echo "running: $(ls $Q/running | tr '\n' ' ')"
echo "done:    $(ls $Q/done | tr '\n' ' ')"; echo "failed:  $(ls $Q/failed | tr '\n' ' ')"
echo "--- queue.log tail"; tail -5 $Q/logs/queue.log
r=$(ls $Q/running | head -1); [ -n "$r" ] && { echo "--- $r log tail"; tail -3 $Q/logs/$r.log; }
echo "gpu: $(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader)"
