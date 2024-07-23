#!/bin/bash
# Register a new user on the server.

# parse command-line arguments
if [[ $# != 3 ]]; then
  echo "usage: $0 <url> <username> <password>"
  exit -1
fi

URL="$1"
USERNAME="$2"
PASSWORD="$3"


# register a new user
curl -s \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" \
  ${URL}/api/users/0

echo
