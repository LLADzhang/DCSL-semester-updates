#!/bin/bash

tmux send-keys -t "mpmcs_reply_server"  C-c 
tmux kill-session -t "mpmcs_reply_server"

tmux send-keys -t "mpmcs_task_scheduler" C-c
tmux kill-session -t "mpmcs_task_scheduler"

tmux ls
