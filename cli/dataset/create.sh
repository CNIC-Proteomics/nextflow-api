#!/bin/bash
# Create a dataset instance on a nextflow server.

# parse command-line arguments
if [[ $# != 2 ]]; then
	echo "usage: $0 <url> <experiment>"
	exit -1
fi

URL="$1"
EXPERIMENT="$2"

# create a dataset instance
curl -s \
	-X POST \
	-d "{\"experiment\":\"${EXPERIMENT}\"}" \
	${URL}/api/datasets/0

echo
