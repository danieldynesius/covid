import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('/home/ph0s/code/.env')

# Access environment variables
gitlab_token = os.getenv("GITLAB_COVID_TOKEN")
user_name = os.getenv("GITLAB_USER")

# Print the loaded variables (optional)
print(f"User Name: {user_name}")

# Configuration
files_to_commit = [
    "/home/ph0s/code/analytics/covid/docs/geo_map.html",
    "/home/ph0s/code/analytics/covid/docs/search_geo.html",
    "/home/ph0s/code/analytics/covid/docs/gtrend_geo_map.html",
    "/home/ph0s/code/analytics/covid/docs/country_trends.html",
    "/home/ph0s/code/analytics/covid/docs/forecasts.html",
    "/home/ph0s/code/analytics/covid/docs/new_research.html"
]

branch_name = "main"
github_username = "danieldynesius"
github_token = os.getenv("GITHUB_TOKEN")  # Read GitHub token from environment variable
gitlab_username = "neutralthinker"
gitlab_repo = "covid"


# Check if GitLab and GitHub tokens are available
if gitlab_token is None:
    print("Error: GitLab token is not set. Please set the GITLAB_TOKEN in the .env file.")
    exit(1)

if github_token is None:
    print("Error: GitHub token is not set. Please set the GITHUB_TOKEN in the .env file.")
    #exit(1)

# Check if files exist
for file in files_to_commit:
    if not os.path.isfile(file):
        print(f"Error: File {file} not found.")
        exit(1)

# Change to the branch
subprocess.run(["git", "checkout", branch_name], check=True)

# Add files to the staging area
for file in files_to_commit:
    subprocess.run(["git", "add", "-f", file], check=True)

# Commit changes
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
commit_message = f"Scheduled data update at {current_datetime}"

try:
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    print("Commit successful.")
except subprocess.CalledProcessError as e:
    print(f"Error during commit: {e.stderr}")
    exit(1)

# Push changes to GitHub (origin)
try:
    subprocess.run(["git", "push", "origin", branch_name], check=True)
    print("Pushed to GitHub (origin) successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error pushing to GitHub: {e.stderr}")
    exit(1)

# Push changes to GitLab (gitlab)
try:
    subprocess.run(["git", "push", "gitlab", branch_name], check=True)
    #subprocess.run(["git", "push", "gitlab", branch_name, "--force"], check=True)
    print("Pushed to GitLab (gitlab) successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error pushing to GitLab: {e.stderr}")
    exit(1)

print("Changes committed and pushed successfully to GitHub and GitLab.")
