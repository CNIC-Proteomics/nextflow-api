#!/bin/bash
# Login a user on the server and retrieve a JWT token.

# parse command-line arguments
if [[ $# != 4 ]]; then
  echo "usage: $0 <url> <username> <password> <token_file>"
  exit -1
fi

URL="$1"
USERNAME="$2"
PASSWORD="$3"
TOKEN_FILE="$4"


# login a user and get a JWT token
OUTPUT=$(curl -s \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" \
  ${URL}/api/login)


# get token
TOKEN=$(echo "$OUTPUT" | sed -n 's/.*"token"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')


# save the token if applied
if [[ ${TOKEN} == "" ]]; then
  echo "Login failed. Please check your username and password."
  exit -1
else
  echo "Login successful. Saving token to ${TOKEN_FILE}"
  echo "${TOKEN}" > "${TOKEN_FILE}"
fi