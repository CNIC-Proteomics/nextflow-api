#!/bin/bash
# Download multiple files for a workflow instance and attempt on a Nextflow server.

# parse command-line arguments
if [[ $# != 4 ]]; then
	echo "usage: $0 <url> <id> <attempt> <data>"
	exit -1
fi

URL="$1"
ID="$2"
ATTEMPT="$3"
DATA="$4"


# download output data for a workflow instance
curl -s \
	-X POST \
	-d "${DATA}" \
	-o "traces-${ID}-${ATTEMPT}.zip" \
	${URL}/api/outputs/multiple/${ID}/${ATTEMPT}/download

echo
