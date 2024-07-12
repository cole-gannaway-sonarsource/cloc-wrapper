# https://github.com/$ORG/$REPO.git

import requests
import csv
import argparse

parser = argparse.ArgumentParser(description='Script to discover Github repositories within a Github organization.')

# Add arguments
parser.add_argument('--organization', type=str, help='Github organization name', required=True)
parser.add_argument('--connectionToken', type=str, help='Github personal access token', required=True)
parser.add_argument('--outputCsv', type=str, help='File path to output a csv file with the necessary information', required=True)

# Parse the arguments
args = parser.parse_args()

organization = args.organization
connectionToken = args.connectionToken
output_csv_file_path = args.outputCsv

# Get repositories in the organization
get_repositories_response = requests.get(f'https://api.github.com/orgs/{organization}/repos?per_page=100&page=1', auth=('', connectionToken))
if get_repositories_response.status_code != 200:
    print('Error: Unable to retrieve repositories from Github')
    exit(1)
get_projects_results = get_repositories_response.json()
with open(f"{output_csv_file_path}", mode='w', newline='') as file:
    writer = csv.writer(file)
    for repo in get_projects_results:
        repo_name = repo["name"]
        print(f'Organization: {organization} and repo: {repo_name}')
        # Create the git clone URL with the connection token for each repository
        clone_url = f"https://oauth2:{connectionToken}@github.com/{organization}/{repo_name}.git"
        repo_id = f"organization-{organization}-repository-{repo_name}"
        # Write the repository id, repository, name and git clone URL to the CSV file
        writer.writerow([repo_id, repo_name, clone_url])


print(f"Wrote results to {output_csv_file_path}")
