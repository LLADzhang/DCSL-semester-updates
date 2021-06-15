#!/bin/bash

for ((i=1;i<=39;i++)); 
do 
    python3 find_user_distribution.py 1min_polling/1min_polling_tasks_result.json $i 
    echo $i
done
