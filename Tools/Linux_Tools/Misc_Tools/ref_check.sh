#!/bin/bash
set -e

end_of_wait=$(date +%s -d "5 minutes")
ssh dhost01 bash <<EOF
	set -ex
	cd /homw/ABC/logs
	while ! grep "Connected to App Engine" *.log
	do
		[[ \$(date +%s) -le ${end_of_wait} ]]
		sleep 5
	done
EOF


