#!/bin/bash
# Create a workflow instance on a nextflow server.

# parse command-line arguments
if [[ $# != 4 ]]; then
	echo "usage: $0 <url> <token_file> <data> <id_file>"
	exit -1
fi

URL="$1"
TOKEN_FILE="$2"
DATA="$3"
ID_FILE="$4"


# read the token from the file
if [[ ! -f "${TOKEN_FILE}" ]]; then
	echo "Token file not found: ${TOKEN_FILE}"
	exit -1
fi
TOKEN=$(cat "${TOKEN_FILE}")


# create a workflow instance
OUTPUT=$(curl -s \
	-X POST \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer ${TOKEN}" \
	-d "${DATA}" \
	${URL}/api/workflows/0)


# get ID
ID=$(echo "$OUTPUT" | sed -n 's/.*"_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')


# save the id if applied
if [[ ${ID} == "" ]]; then
  echo "Query failed. Please check your parameters. Error: ${OUTPUT}"
  exit -1
else
  echo "Query successful. Saving ID to ${ID_FILE}"
  echo "${ID}" > "${ID_FILE}"
fi
