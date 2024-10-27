#!/bin/bash

# Configuration
files_to_commit=(
  "/home/ph0s/code/analytics/covid/docs/geo_map.html"
  "/home/ph0s/code/analytics/covid/docs/search_geo.html"
  "/home/ph0s/code/analytics/covid/docs/gtrend_geo_map.html"
  "/home/ph0s/code/analytics/covid/docs/country_trends.html"
  "/home/ph0s/code/analytics/covid/docs/forecasts.html"
  "/home/ph0s/code/analytics/covid/docs/new_research.html"
)

branch_name="main"
github_username="danieldynesius"
github_token="$GITHUB_TOKEN"  # Use environment variable
github_repo="covid"

gitlab_username="your_gitlab_username"
gitlab_token="$GITLAB_TOKEN"  # Use environment variable
gitlab_repo="your_gitlab_repo_name"

push_to_gitlab() {
  # Set GitLab remote URL
  gitlab_remote_url="https://${gitlab_username}:${gitlab_token}@gitlab.com/${gitlab_username}/${gitlab_repo}.git"
  
  # Add GitLab as a remote
  git remote add gitlab $gitlab_remote_url
  
  # Push to GitLab
  git push gitlab "$branch_name"
  
  # Remove GitLab remote to keep things clean
  git remote remove gitlab
}

for file in "${files_to_commit[@]}"; do
  git add "$file"
done

commit_message="Scheduled data update"
current_datetime=$(date +"%Y-%m-%d %H:%M:%S")
commit_message="Scheduled data update at $current_datetime"

# Check if the files exist
for file in "${files_to_commit[@]}"; do
  if [ ! -f "$file" ]; then
    echo "Error: File $file not found."
    exit 1
  fi
done

# Change to branch
git checkout "$branch_name"

# Add the files to the staging area
git add -f "${files_to_commit[@]}"

# Commit changes
git commit -m "$commit_message"

# Push changes to GitHub
git push origin "$branch_name"

# Push changes to GitLab
push_to_gitlab

echo "Changes committed and pushed successfully to GitHub and GitLab."
