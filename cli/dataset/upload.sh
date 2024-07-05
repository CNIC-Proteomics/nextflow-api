#!/bin/bash
# Upload dataset data for a dataset instance on a nextflow server.

# parse command-line arguments
if [[ $# != 5 ]]; then
	echo "usage: $0 <url> <id> <format> <parameter> <filename>"
	exit -1
fi

URL="$1"
ID="$2"
FORMAT="$3"
PARAMETER="$4"
FILENAME="$5"

# upload data to a dataset instance
curl -s \
	-F "filename=$(basename FILENAME)" \
	-F "body=@${FILENAME}" \
	${URL}/api/datasets/${ID}/${FORMAT}/${PARAMETER}/upload

echo
