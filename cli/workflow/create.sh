#!/bin/bash
# Create a workflow instance on a nextflow server.

# parse command-line arguments
if [[ $# != 2 ]]; then
	echo "usage: $0 <url> <data>"
	exit -1
fi

URL="$1"
DATA="$2"

# create a workflow instance
curl -s \
	-X POST \
	-d "${DATA}" \
	${URL}/api/workflows/0

echo
