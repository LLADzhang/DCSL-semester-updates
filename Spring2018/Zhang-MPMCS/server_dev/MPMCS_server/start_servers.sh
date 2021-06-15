#!/bin/bash

tmux new -s "mpmcs_reply_server" -d
tmux send-keys -t "mpmcs_reply_server" "python3 mpmcs_reply_server.py" C-m

tmux new -s "mpmcs_task_scheduler" -d
tmux send-keys -t "mpmcs_task_scheduler" "perf stat -d python3 mpmcs_task_scheduler.py" C-m
tmux ls
