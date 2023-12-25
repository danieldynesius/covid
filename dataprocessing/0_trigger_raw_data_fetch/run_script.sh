#!/bin/bash

# Your Python script path
python_script='/home/stratega/code/analytics/covid/dataprocessing/0_trigger_raw_data_fetch/fetch_raw.py'

# Flag file path
flag_file="/home/stratega/code/analytics/covid/dataprocessing/0_trigger_raw_data_fetch/flag_file.txt"

# Check if the flag file exists (indicating the script has already run today)
if [ -f "$flag_file" ]; then
    echo "Script already executed today."
else
    # Run the Python script
    python3 "$python_script"

    # Create/update the flag file
    touch "$flag_file"
    echo "Script executed on $(date)" > "$flag_file"
fi
