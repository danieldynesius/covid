#!/bin/bash

# Read the config file
CONFIG_FILE="/home/stratega/code/analytics/covid/conf.ini"
# Read the [BasePaths] section
BASE_PATH=$(grep '^\s*base_path' "${CONFIG_FILE}" | awk -F '=' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')

# Function to replace placeholders with values
interpolate() {
    echo "$1" | sed "s#%(base_path)s#${BASE_PATH}#g"
}

# Accessing values
raw_datapath=$(interpolate "$(grep '^\s*raw_datapath' "${CONFIG_FILE}" | awk -F '=' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')")
raw_script=$(interpolate "$(grep '^\s*raw_script' "${CONFIG_FILE}" | awk -F '=' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')")

staged_scripts=$(interpolate "$(grep '^\s*staged_scripts' "${CONFIG_FILE}" | awk -F '=' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')")
final_geo_script=$(interpolate "$(grep '^\s*final_geo_script' "${CONFIG_FILE}" | awk -F '=' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')")
final_trend_script=$(interpolate "$(grep '^\s*final_trend_script' "${CONFIG_FILE}" | awk -F '=' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')")
final_write_dir=$(interpolate "$(grep '^\s*final_write_dir' "${CONFIG_FILE}" | awk -F '=' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')")
push_html_file=$(interpolate "$(grep '^\s*push_html_file' "${CONFIG_FILE}" | awk -F '=' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')")

# Now you can use these variables in your shell script
echo "basepath: ${BASE_PATH}"
echo "raw_datapath: ${raw_datapath}"
echo "raw_script: ${raw_script}"
echo "staged_scripts: ${staged_scripts}"
echo "final_geo_script: ${final_geo_script}"
echo "final_trend_script: ${final_trend_script}"
echo "final_write_dir: ${final_write_dir}"
echo "push_html_file: ${push_html_file}"