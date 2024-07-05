#!/bin/bash
# Get a list of all outputs for a workflow intance and attempt on a nextflow server.

# parse command-line arguments
if [[ $# != 3 ]]; then
	echo "usage: $0 <url> <id> <attempt>"
	exit -1
fi

URL="$1"
ID="$2"
ATTEMPT="$3"

# get a output instance
curl -s \
	-X GET \
	${URL}/api/outputs/${ID}/${ATTEMPT}

echo
