#!/bin/bash
# Collect output data into a single archive.

# parse command-line arguments
if [[ $# != 3 ]]; then
	echo "usage: $0 <id> <attempt> <path>"
	exit -1
fi

ID="$1"
ATTEMPT="$2"
SRC_PATH="$3"
DST_DIRNAME="$(dirname ${SRC_PATH})"

# replace any links with the original files
for f in $(find ${SRC_PATH} -type l); do
	cp --remove-destination $(readlink $f) $f
done

# copy log file into output folder
# cp ${DST_DIRNAME}/.workflow.log ${SRC_PATH}/workflow.log

# # remove old nextflow reports (except for logs)
# rm -f ${SRC_PATH}/reports/report.html.*
# rm -f ${SRC_PATH}/reports/timeline.html.*
# rm -f ${SRC_PATH}/reports/trace.txt.*

# create archive of output data
cd ${DST_DIRNAME} && tar -czf "outputs-${ID}-${ATTEMPT}.tar.gz" $(basename ${SRC_PATH})/*
# cd ${SRC_PATH} && tar -czf "../outputs-${ID}-${ATTEMPT}.tar.gz" *
