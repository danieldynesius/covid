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
    trigger_path = "/home/stratega/code/analytics/covid/dataprocessing/1_fetch_data_write_to_raw"
    log_output_path = "/home/stratega/code/analytics/covid/dataprocessing/0_trigger_raw_data_fetch/log.txt"
    run_scripts_in_folder(trigger_path, log_output_path)
