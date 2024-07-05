#!/bin/bash
# Launch a workflow instance on a nextflow server.

# parse command-line arguments
if [[ $# != 3 ]]; then
	echo "usage: $0 <url> <id> <data>"
	exit -1
fi

URL="$1"
ID="$2"
DATA="$3"

# launch a workflow instance
curl -s \
	-X POST \
	-d "${DATA}" \
	${URL}/api/workflows/${ID}/launch

echo
