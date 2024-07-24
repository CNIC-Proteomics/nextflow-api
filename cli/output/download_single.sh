#!/bin/bash
# Download data using the provided file names for a workflow instance and attempt on a Nextflow server.

# parse command-line arguments
if [[ $# != 5 ]]; then
	echo "usage: $0 <url> <token_file> <id_file> <attempt> <file>"
	exit -1
fi

URL="$1"
TOKEN_FILE="$2"
ID_FILE="$3"
ATTEMPT="$4"
FILE="$5"


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



# Extract the file name using basename
FNAME=$(basename "${FILE}")



# download output data for a workflow instance
curl -s \
	-H "Authorization: Bearer ${TOKEN}" \
	-o "${FNAME}" \
	${URL}/api/outputs/single/${ID}/${ATTEMPT}/${FILE}/download

echo
