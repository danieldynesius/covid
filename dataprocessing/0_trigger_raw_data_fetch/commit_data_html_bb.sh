#!/bin/bash

# Load .env !
source "/home/ph0s/code/analytics/covid-bitbucket/covid/.env"
echo "BITBUCKET_USERNAME: $BITBUCKET_USERNAME"
echo "BITBUCKET_APP_PASSWORD: $BITBUCKET_APP_PASSWORD"

# Configuration
files_to_commit=(
  "/home/ph0s/code/analytics/covid/docs/geo_map.html"
  "/home/ph0s/code/analytics/covid/docs/search_geo.html"
  "/home/ph0s/code/analytics/covid/docs/gtrend_geo_map.html"
  "/home/ph0s/code/analytics/covid/docs/country_trends.html"
  "/home/ph0s/code/analytics/covid/docs/forecasts.html"
  "/home/ph0s/code/analytics/covid/docs/new_research.html"
)

for file in "${files_to_commit[@]}"; do
  git add -f "$file"
done

commit_message="Scheduled data update"
current_datetime=$(date +"%Y-%m-%d %H:%M:%S")
commit_message="Scheduled data update at $current_datetime"

branch_name="main"
bitbucket_username=$BITBUCKET_USERNAME
bitbucket_password=$BITBUCKET_APP_PASSWORD

bitbucket_repo="covidfox/covid"

# Check if the file exists
if [ ! -f "$files_to_commit" ]; then
    echo "Error: File $files_to_commit not found."
    exit 1
fi

# Change to the specified branch
git checkout "$branch_name"

# Add the file to the staging area
git add -f "${files_to_commit[@]}"
#git add "${files_to_commit[@]}"

# Commit changes
git commit -m "$commit_message"

# Push changes to the specified branch on Bitbucket
#git push https://danieldynesius@bitbucket.org/covidfox/covid.git "$branch_name"
git push https://$BITBUCKET_USERNAME:$BITBUCKET_APP_PASSWORD@bitbucket.org/$bitbucket_repo.git "$branch_name"

echo "Changes committed and pushed successfully."