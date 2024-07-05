#!/bin/bash
# Delete the outputs for a workflow intance and attempt on a nextflow server.

# parse command-line arguments
if [[ $# != 3 ]]; then
	echo "usage: $0 <url> <id> <attempt>"
	exit -1
fi

URL="$1"
ID="$2"
ATTEMPT="$3"

# delete outputs for a workflow intance and attempt
curl -s \
	-X DELETE \
	${URL}/api/outputs/${ID}/${ATTEMPT}

echo
