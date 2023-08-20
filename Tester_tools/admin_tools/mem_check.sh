#!/bin/bash

## run : nohup mem_check.sh &> mem_dump_$(date -I)

while [[ true ]];do
	echo "======================================"
	date +%Y-%m-%d-%H:%M:%S
	free -hwt
	echo -e "\n"
	ps aux --sort -rss |pr -TW 256|head -15
	
	#Collect stats every 2min
	sleep 120;
done
