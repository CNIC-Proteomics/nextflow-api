#!/bin/bash
# Get a list of all shared volumes for a given path on a nextflow server.

# parse command-line arguments
if [[ $# -lt 2 ]]; then
	echo "usage: $0 <url> <token_file> <path>"
	exit -1
fi

URL="$1"
TOKEN_FILE="$2"
VOLUME_PATH="$3"


# read the token from the file
if [[ ! -f "${TOKEN_FILE}" ]]; then
	echo "Token file not found: ${TOKEN_FILE}"
	exit -1
fi
TOKEN=$(cat "${TOKEN_FILE}")



# get a volume instance
curl -s \
	-X GET \
	-H "Authorization: Bearer ${TOKEN}" \
	${URL}/api/volumes/${VOLUME_PATH}

echo
