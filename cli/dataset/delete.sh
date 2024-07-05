#!/bin/bash
# Delete a dataset instance on a nextflow server.

# parse command-line arguments
if [[ $# != 2 ]]; then
	echo "usage: $0 <url> <id>"
	exit -1
fi

URL="$1"
ID="$2"

# delete a dataset instance
curl -s -X DELETE ${URL}/api/datasets/${ID}

echo
