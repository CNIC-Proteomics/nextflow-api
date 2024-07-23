#!/bin/bash
# Edit a user instance on a nextflow server.

# parse command-line arguments
if [[ $# != 4 ]]; then
	echo "usage: $0 <url> <token_file> <user_name> <data>"
	exit -1
fi

URL="$1"
TOKEN_FILE="$2"
USER_NAME="$3"
DATA="$4"


# read the token from the file
if [[ ! -f "${TOKEN_FILE}" ]]; then
	echo "Token file not found: ${TOKEN_FILE}"
	exit -1
fi
TOKEN=$(cat "${TOKEN_FILE}")



# update a user instance
curl -s \
	-X POST \
	-H "Authorization: Bearer ${TOKEN}" \
	-d "${DATA}" \
	${URL}/api/users/${USER_NAME}

echo
