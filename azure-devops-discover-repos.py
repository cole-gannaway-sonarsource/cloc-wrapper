import requests
import csv
import argparse

parser = argparse.ArgumentParser(description='Script to discover Azure DevOps repositories within an Azure DevOps organization.')

# Add arguments
parser.add_argument('--organization', type=str, help='Azure DevOps organization name', required=True)
parser.add_argument('--connectionToken', type=str, help='Azure DevOps personal access token', required=True)
parser.add_argument('--outputCsv', type=str, help='File path to output a csv file with the necessary information', required=True)

# Parse the arguments
args = parser.parse_args()

organization = args.organization
connectionToken = args.connectionToken
output_csv_file_path = args.outputCsv

# Get projects in the organization
get_projects_response = requests.get(f'https://dev.azure.com/{organization}/_apis/projects?api-version=7.0', auth=('', connectionToken))
if get_projects_response.status_code != 200:
    print(f'Error: Unable to retrieve projects from Azure DevOps. Status code: {get_projects_response.status_code}, Reason: {get_projects_response.reason}')
    exit(1)

get_projects_results = get_projects_response.json()
with open(f"{output_csv_file_path}", mode='w', newline='') as file:
    writer = csv.writer(file)
    for project in get_projects_results["value"]:
        project_name = project["name"]
        # Get the repositories in each project
        repo_response = requests.get(f'https://dev.azure.com/{organization}/{project_name}/_apis/git/repositories?api-version=7.0', auth=('', connectionToken))
        if repo_response.status_code != 200:
            print(f'Error: Unable to retrieve repositories from Azure DevOps project {project_name}')
        repo_results = repo_response.json()
        for repo in repo_results["value"]:
            repo_name = repo["name"]
            print(f"Organization: {organization}    project: {project_name}    repo: {repo_name}")
            # Create the git clone URL with the connection token for each repository
            clone_url = f"https://{connectionToken}@dev.azure.com/{organization}/{project_name}/_git/{repo_name}"
            repo_id = f"organization-{organization}-project-{project_name}-repository-{repo_name}"
            # Write the repository id, repository, name and git clone URL to the CSV file
            writer.writerow([repo_id, repo_name, clone_url])

print(f"Wrote results to {output_csv_file_path}")

