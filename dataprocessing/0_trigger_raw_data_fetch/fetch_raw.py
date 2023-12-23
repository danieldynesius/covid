import os
import subprocess
from datetime import datetime

def run_scripts_in_folder(trigger_path, log_output_path):
    script_files = [file for file in os.listdir(trigger_path) if file.endswith(".py")]

    with open(log_output_path, "w") as log_file:
        log_file.write("")

    with open(log_output_path, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"---------------------[ Dataload Triggered: {timestamp} ]----------------------\n")
        for script_file in script_files:
            script_path = os.path.join(trigger_path, script_file)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                subprocess.run(["python", script_path], check=True)
                log_file.write(f"{timestamp} - {script_file} - OK\n")
            except subprocess.CalledProcessError as e:
                log_file.write(f"{timestamp} - {script_file} - Fail\n")
                log_file.write(f"Error: {e}\n")

if __name__ == "__main__":
    trigger_path = "home/stratega/code/analytics/covid/dataprocessing/1_fetch_data_write_to_raw"
    log_output_path = "home/stratega/analytics/covid/dataprocessing/0_trigger_raw_data_fetch/log.txt"
    run_scripts_in_folder(trigger_path, log_output_path)



import os
import time
from datetime import datetime
import pandas as pd

def extract_country_name(file_path):
    # Get the last part of the path after the last '/'
    last_part = file_path.split('/')[-1]

    # Extract the first word (country name) before the '.'
    country_name = last_part.split('.')[0]

    # Extract the first word before the first "_"
    first_word = country_name.split('_')[0]

    return first_word

def convert_timestamp_to_datetime(timestamp):
    # Convert timestamp to datetime object
    date_object = datetime.fromtimestamp(timestamp)
    
    # Format the datetime object to '%Y-%m-%d %H:%M:%S'
    formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_date

def find_old_files(directory, hours_threshold=24):
    files_data = {"country": [], "last_modified_date": [], "needs_update_flg": []}

# Step 1: Check for latest update per raw datafile

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Check if it's a regular file (not a directory or a special file)
        if os.path.isfile(file_path):
            # Get the last modification time of the file
            last_modified_time = os.path.getmtime(file_path)

            # Get the current time
            current_time = time.time()

            # Calculate the time difference in seconds
            time_difference = current_time - last_modified_time

            # Convert the time difference to hours
            time_difference_hours = time_difference / 3600

            # Extract the country name
            country_name = extract_country_name(file_path)

            # Convert last modification time to formatted date
            last_modified_date = convert_timestamp_to_datetime(last_modified_time)

            # Append data to the dictionary
            files_data["country"].append(country_name) # Only include the first word in the country column
            files_data["last_modified_date"].append(last_modified_date)
            files_data["needs_update_flg"].append(time_difference_hours > hours_threshold)

    # Create a DataFrame from the dictionary
    files_df = pd.DataFrame(files_data)

    return files_df

# Example usage:
datapath = '/home/stratega/code/analytics/covid/data/1_raw_data'
files_df = find_old_files(datapath)

# Display the DataFrame
files_df
