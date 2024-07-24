#!/bin/bash
# Delete a dataset instance on a nextflow server.

# parse command-line arguments
if [[ $# != 3 ]]; then
	echo "usage: $0 <url> <token_file> <id_file>"
	exit -1
fi

URL="$1"
TOKEN_FILE="$2"
ID_FILE="$3"


# read the token from the file
if [[ ! -f "${TOKEN_FILE}" ]]; then
	echo "Token file not found: ${TOKEN_FILE}"
	exit -1
fi
TOKEN=$(cat "${TOKEN_FILE}")



# read the token from the file
if [[ ! -f "${ID_FILE}" ]]; then
	echo "Id file not found: ${ID_FILE}"
	exit -1
fi
ID=$(cat "${ID_FILE}")



# delete a dataset instance
curl -s \
	-X DELETE \
	-H "Authorization: Bearer ${TOKEN}" \
	${URL}/api/datasets/${ID}

echo
