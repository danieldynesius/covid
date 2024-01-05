#!/bin/bash

# Configuration
#"/home/stratega/code/analytics/covid/docs/geo_map.html"
files_to_commit=(
  "/home/stratega/code/analytics/covid/docs/country_trends.html"
)

for file in "${files_to_commit[@]}"; do
  git add "$file"
done

commit_message="Scheduled data update"
current_datetime=$(date +"%Y-%m-%d %H:%M:%S")
commit_message="Scheduled data update at $current_datetime"

#branch_name="gh-pages"
branch_name="main"
github_username="danieldynesius"
github_token="$GITHUB_TOKEN"  # Use environment variable
github_repo="covid"

# Check if the file exists
if [ ! -f "$files_to_commit" ]; then
    echo "Error: File $files_to_commit not found."
    exit 1
fi

# Chg to branch gh-pages
git checkout "$branch_name"

# Add the file to the staging area
git add -f "$files_to_commit"

# Commit changes
git commit -m "$commit_message"

# Push changes to the specified branch
git push origin "$branch_name"

# GitHub API URL
github_api_url="https://api.github.com/repos/$github_username/$github_repo/pulls"

# Create a pull request using GitHub API (optional)
# Uncomment the following lines if you want to create a pull request
# Pull requests require a forked repository and may need additional configurations

# pull_request_title="<your_pull_request_title>"
# pull_request_body="<your_pull_request_description>"
# pull_request_base_branch="<your_target_branch>"
# pull_request_head_branch="$branch_name"

# curl -X POST \
#     -H "Authorization: token $github_token" \
#     -H "Content-Type: application/json" \
#     -d "{\"title\":\"$pull_request_title\",\"body\":\"$pull_request_body\",\"base\":\"$pull_request_base_branch\",\"head\":\"$pull_request_head_branch\"}" \
#     $github_api_url

echo "Changes committed and pushed successfully."
