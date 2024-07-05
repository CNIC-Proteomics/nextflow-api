#!/bin/bash
# Retrieve all data (all files) for a workflow instance and attempt on a nextflow server.

# parse command-line arguments
if [[ $# != 3 ]]; then
	echo "usage: $0 <url> <id> <attempt>"
	exit -1
fi

URL="$1"
ID="$2"
ATTEMPT="$3"

# download output data for a workflow instance
curl -s \
	-o "outputs-${ID}-${ATTEMPT}.tar.gz" \
	${URL}/api/outputs/archive/${ID}/${ATTEMPT}/download

echo
