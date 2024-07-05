#!/bin/bash
# List all dataset instances on a nextflow server.

# parse command-line arguments
if [[ $# != 1 ]]; then
	echo "usage: $0 <url>"
	exit -1
fi

URL="$1"

# list all dataset instances
curl -s -X GET ${URL}/api/datasets

echo
