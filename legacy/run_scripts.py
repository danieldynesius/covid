#!/usr/bin/env python3
import subprocess
import os
from datetime import datetime
import configparser

# Read the INI file
config_file = '/home/ph0s/code/analytics/covid/conf.ini'

# Read the INI file
config = configparser.ConfigParser()
config.read(config_file)

# Get values from the [Paths] section
base_path = config.get('Paths', 'base_path')
raw_datapath = config.get('Paths', 'raw_datapath')
trigger_raw_scripts = config.get('Paths', 'trigger_raw_scripts')
flag_file = config.get('Paths', 'flag_file')
staged_scripts = config.get('Paths', 'staged_scripts')
final_geo_script = config.get('Paths', 'final_geo_script')
final_trend_script = config.get('Paths', 'final_trend_script')
final_write_dir = config.get('Paths', 'final_write_dir')
push_html_file = config.get('Paths', 'push_html_file')
data_stale_hours = config.getint('Data', 'data_stale_hours')

# Print the values for verification
print(f"base_path: {base_path}")
print(f"raw_datapath: {raw_datapath}")
print(f"trigger_raw_scripts: {trigger_raw_scripts}")
print(f"flag_file: {flag_file}")
print(f"staged_scripts: {staged_scripts}")
print(f"final_geo_script: {final_geo_script}")
print(f"final_trend_script: {final_trend_script}")
print(f"final_write_dir: {final_write_dir}")
print(f"push_html_file: {push_html_file}")
print(f"data_stale_hours: {data_stale_hours}")


# Activate the virtual environment
venv_activate_script = os.path.join(base_path, 'venv/covid-dash/bin/activate')
subprocess.run(f"source {venv_activate_script} && deactivate", shell=True)

# Check if the flag file exists (indicating the script has already run today)
if os.path.isfile(flag_file):
    with open(flag_file, 'r') as file:
        lines = file.readlines()
        if lines:
            latest_runtime = lines[-1].split(' ', 3)[-1].strip()
            print(f"Latest runtime: {latest_runtime}")
        else:
            print("Script has not been executed today.")

    # Prompt user to confirm running the script
    choice = input("Do you want to run the script anyway? (y/n): ").lower()
    if choice != "y":
        print("Script not executed.")
        exit(0)

# Run the Python script
subprocess.run(['python3', trigger_raw_scripts])

# Create/update the flag file
with open(flag_file, 'a') as file:
    file.write(f"Script executed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print(f"basepath: {base_path}")
print(f"raw_datapath: {raw_datapath}")
print(f"trigger_raw_scripts: {trigger_raw_scripts}")
print(f"flag_file: {flag_file}")
print(f"staged_scripts: {staged_scripts}")
print(f"final_geo_script: {final_geo_script}")
print(f"final_trend_script: {final_trend_script}")
print(f"final_write_dir: {final_write_dir}")
print(f"push_html_file: {push_html_file}")
print(f"data_stale_hours: {data_stale_hours}")
