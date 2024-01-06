import os
import subprocess
from datetime import datetime
import time
import pandas as pd
import configparser

#----------------------------------------------------------------------------------------------
# Step 0: Read Config file
#----------------------------------------------------------------------------------------------
config_file = '/home/stratega/code/analytics/covid/conf.ini'

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

trigger_path = config.get('Paths', 'trigger_path')
log_output_path = config.get('Paths', 'log_output_path')

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
#subprocess.run(['python3', trigger_raw_scripts])

# Create/update the flag file
with open(flag_file, 'a') as file:
    file.write(f"Script executed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


#----------------------------------------------------------------------------------------------
# Step 1: Check Which Countrie's Data Need to be Updated
#----------------------------------------------------------------------------------------------

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

def data_freshness(directory, hours_threshold=data_stale_hours):
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



file_df = data_freshness(raw_datapath)

# Display the DataFrame
file_df


#----------------------------------------------------------------------------------------------
# Step 2: Update Needed Data
#----------------------------------------------------------------------------------------------

def run_scripts_in_folder(trigger_path, log_output_path):
    script_files = [file for file in os.listdir(trigger_path) if file.endswith(".py")]

    # Iterate over script files
    
    for script_file in script_files:
        # Check if part of the file name exists in the 'country' column where 'needs_update_flg' is True
        for index, row in file_df[file_df['needs_update_flg']==True].iterrows():
            if row['country'] in script_file:
                print(f"'{script_file}' will trigger.")
    
    with open(log_output_path, "w") as log_file:
        log_file.write("")

    with open(log_output_path, "a") as log_file:
        load_tstamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"---------------------[ Dataload Triggered: {load_tstamp} ]----------------------\n")
        for script_file in script_files:
            print('Triggering:', script_file)
            script_path = os.path.join(trigger_path, script_file)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                subprocess.run(["python", script_path], check=True)
                log_file.write(f"{timestamp} - {script_file} - OK\n")
            except subprocess.CalledProcessError as e:
                log_file.write(f"{timestamp} - {script_file} - Fail\n")
                log_file.write(f"Error: {e}\n")
    
    return load_tstamp

if __name__ == "__main__":
    #trigger_path = "/home/stratega/code/analytics/covid/dataprocessing/1_fetch_data_write_to_raw"
    #log_output_path = "/home/stratega/code/analytics/covid/dataprocessing/0_trigger_raw_data_fetch/log.txt"
    load_tstamp = run_scripts_in_folder(trigger_path, log_output_path)

#----------------------------------------------------------------------------------------------
# Step 3: Check Data Updated & Save to Output Dir
#----------------------------------------------------------------------------------------------
file_df = data_freshness(raw_datapath)
file_df.to_csv(f'{raw_datapath}/data_freshness.csv',index=False)



#----------------------------------------------------------------------------------------------
# Step 4: Run Staged Scripts
#----------------------------------------------------------------------------------------------


def run_scripts_in_stage(trigger_path, log_output_path):
    script_files = [file for file in os.listdir(trigger_path) if file.endswith(".py")]

    # Iterate over script files
    
    for script_file in script_files:
        # Check if part of the file name exists in the 'country' column where 'needs_update_flg' is True
        for index, row in file_df[file_df['needs_update_flg']==True].iterrows():
            if row['country'] in script_file:
                print(f"'{script_file}' will trigger.")

    # Dont make New File
#    with open(log_output_path, "w") as log_file:
 #       log_file.write("")

    with open(log_output_path, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"---------------------[ Stage Transformation: {timestamp} ]----------------------\n")
        for script_file in script_files:
            print('Triggering:', script_file)
            script_path = os.path.join(trigger_path, script_file)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                subprocess.run(["python", script_path], check=True)
                log_file.write(f"{timestamp} - {script_file} - OK\n")
            except subprocess.CalledProcessError as e:
                log_file.write(f"{timestamp} - {script_file} - Fail\n")
                log_file.write(f"Error: {e}\n")


run_scripts_in_stage(staged_scripts, log_output_path)


#----------------------------------------------------------------------------------------------
# Step 5: Run Final Scripts
#----------------------------------------------------------------------------------------------

# Run it
subprocess.run(["python", final_geo_script], check=True) # Geo Map
subprocess.run(["python", final_trend_script], check=True) # Trend Charts


#----------------------------------------------------------------------------------------------
# Step 6: Save latest load timestamp
#----------------------------------------------------------------------------------------------

# Write the load data timestamp
pd.DataFrame(
    {'latest_dataload': [load_tstamp]}
    ).to_csv(final_write_dir+'latest_dataload.csv'
    ,index=False)

#----------------------------------------------------------------------------------------------
# Step 7: Trigger shell script
#----------------------------------------------------------------------------------------------


# Run the shell script
subprocess.run(['bash', push_html_file])