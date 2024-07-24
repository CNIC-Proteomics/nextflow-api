#!/bin/bash
# List all dataset instances on a nextflow server.

# parse command-line arguments
if [[ $# != 2 ]]; then
    echo "usage: $0 <url> <token_file>"
    exit -1
fi

URL="$1"
TOKEN_FILE="$2"


# read the token from the file
if [[ ! -f "${TOKEN_FILE}" ]]; then
	echo "Token file not found: ${TOKEN_FILE}"
	exit -1
fi
TOKEN=$(cat "${TOKEN_FILE}")


# list all dataset instances
curl -s \
	-X GET \
	-H "Authorization: Bearer ${TOKEN}" \
	${URL}/api/datasets

echo
