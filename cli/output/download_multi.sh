#!/bin/bash
# Download multiple files for a workflow instance and attempt on a Nextflow server.

# parse command-line arguments
if [[ $# != 5 ]]; then
	echo "usage: $0 <url> <token_file> <id_file> <attempt> <data>"
	exit -1
fi

URL="$1"
TOKEN_FILE="$2"
ID_FILE="$3"
ATTEMPT="$4"
DATA="$5"


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



# download output data for a workflow instance
curl -s \
	-X POST \
	-H "Authorization: Bearer ${TOKEN}" \
	-d "${DATA}" \
	-o "traces-${ID}-${ATTEMPT}.zip" \
	${URL}/api/outputs/multiple/${ID}/${ATTEMPT}/download

echo
