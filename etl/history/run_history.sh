#!/bin/bash

# Usage
# ./run_history <start_date> <end_date>

set -e

start_date=$1
end_date=$2

local_start_date="20250117"
local_end_date="20250212"
s3_start_date="20250203"
s3_end_date="20250212"

srcdir="data/"

current_date=$start_date
while [ "$current_date" -le "$local_end_date" ]; do
    printf "Starting ${current_date} (local)"
    python lib/process1d.py "$current_date" --srcdir "$srcdir"
    current_date=$(date -d "$current_date + 1 day" +%Y%m%d)
done

while [ "$current_date" -ge $s3_start_date ] && [ "$current_date" -le "$s3_end_date" ]; do
    printf "Starting ${current_date} (s3)"
    python lib/process1d.py "$current_date"
    current_date=$(date -d "$current_date + 1 day" +%Y%m%d)
done

printf "Done"

