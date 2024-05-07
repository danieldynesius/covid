#!/bin/bash

# Activate the virtual environment
source /home/ph0s/code/venv/covid-dash/bin/activate

# Your Python script path
python_script='/home/ph0s/code/analytics/covid/dataprocessing/0_trigger_raw_data_fetch/fetch_raw.py'

# Flag file path
flag_file="/home/ph0s/code/analytics/covid/dataprocessing/0_trigger_raw_data_fetch/flag_file.txt"

# Function to get the latest runtime
get_latest_runtime() {
    if [ -f "$flag_file" ]; then
        latest_runtime=$(tail -n 1 "$flag_file" | cut -d ' ' -f 4-)
        echo "Latest runtime: $latest_runtime"
    else
        echo "Script has not been executed today."
    fi
}

# Check if the flag file exists (indicating the script has already run today)
if [ -f "$flag_file" ]; then
    get_latest_runtime

    # Prompt user to confirm running the script
    read -p "Do you want to run the script anyway? (y/n): " choice
    if [ "$choice" != "y" ]; then
        echo "Script not executed."
        exit 0
    fi
fi

# Run the Python script
python3 "$python_script"

# Create/update the flag file
touch "$flag_file"
echo "Script executed on $(date)" >> "$flag_file"

get_latest_runtime
