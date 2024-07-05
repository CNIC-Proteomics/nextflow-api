#!/bin/bash
# Download data using the provided file names for a workflow instance and attempt on a Nextflow server.

# parse command-line arguments
if [[ $# != 4 ]]; then
	echo "usage: $0 <url> <id> <attempt> <file>"
	exit -1
fi

URL="$1"
ID="$2"
ATTEMPT="$3"
FILE="$4"

# Extract the file name using basename
FNAME=$(basename "${FILE}")


# download output data for a workflow instance
curl -s \
	-o "${FNAME}" \
	${URL}/api/outputs/single/${ID}/${ATTEMPT}/${FILE}/download

echo
