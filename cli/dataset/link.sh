#!/bin/bash
# Link dataset data for a dataset instance on a nextflow server.

# parse command-line arguments
if [[ $# != 4 ]]; then
	echo "usage: $0 <url> <token_file> <id_file> <data>"
	exit -1
fi

URL="$1"
TOKEN_FILE="$2"
ID_FILE="$3"
DATA="$4"



# read the token from the file
if [[ ! -f "${TOKEN_FILE}" ]]; then
	echo "Token file not found: ${TOKEN_FILE}"
	exit -1
fi
TOKEN=$(cat "${TOKEN_FILE}")



# read the id from the file
if [[ ! -f "${ID_FILE}" ]]; then
	echo "Id file not found: ${ID_FILE}"
	exit -1
fi
ID=$(cat "${ID_FILE}")



# link data to a dataset instance
curl -s \
	-X POST \
	-H "Authorization: Bearer ${TOKEN}" \
	-d "${DATA}" \
	${URL}/api/datasets/${ID}/link

echo
