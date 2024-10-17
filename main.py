import requests
import json
import argparse
import os
import shutil
import stat

def sanitize_path(path):
    if os.name == "nt": # check if os is windows
        return f'"{path}"'
    return path

parser = argparse.ArgumentParser(description='Script to discover Github repositories within a Github organization.')

# Add arguments
parser.add_argument('--organization', type=str, help='Github organization name', required=True)
parser.add_argument('--access_token', type=str, help='Github personal access token', required=True)
parser.add_argument('--use_http', action='store_true', help='Use HTTP instead of HTTPS', required=False)
parser.add_argument('--devops_base_url_override', type=str, help='Overrides the base URL for the DevOps provider. Defaults will be github.com, dev.azure.com, bitbucket.org, or gitlab.com. However, you can override this with your own self-hosted ip or domain', required=False)
parser.add_argument('--devops', type=str, help='GitHub, AzureDevOps, Bitbucket, GitLab, or Local', required=True)
parser.add_argument('--clocPath', type=str, help="Path to cloc executable. Default is 'cloc'", required=False, default="cloc")

# Parse the arguments
args = parser.parse_args()

# Assign the arguments to variables
organization = args.organization
access_token = args.access_token
use_http = args.use_http
devops_base_url_override = args.devops_base_url_override
devops = args.devops
path_to_cloc = sanitize_path(args.clocPath)

# set global variables
print(f'Use https: {use_http}, {args.use_http}')
http_protocol = 'https'
if use_http == True:
    http_protocol = 'http'

class RepoInfo:
    def __init__(self, organization: str, project: str, repository_name: str, default_branch: str, clone_url: str):
        # Github does not have a concept of projects
        if project == "":
            self.id = f"{organization}-{repository_name}"
        else:
            self.id = f"{organization}-{project}-{repository_name}"
        
        self.repository_name = repository_name
        self.organization_name = organization
        self.project_name = project
        self.default_branch = default_branch
        self.clone_url = clone_url

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "repository_name": self.repository_name,
            "organization_name": self.organization_name,
            "project_name": self.project_name,
            "default_branch": self.default_branch,
            "clone_url" : self.clone_url
        }
    
def inject_access_token_into_clone_url(auth_protocol: str,clone_url: str, access_token: str) -> str:
    # remove the http:// or https://
    prefix_to_remove = f"{http_protocol}://"
    prefixed_removed_clone_url = clone_url.removeprefix(prefix_to_remove)
    # inject the access token
    # example: https://oauth2:accessToken@github.com/organization/repoName.git
    return f"{prefix_to_remove}{auth_protocol}:{access_token}@{prefixed_removed_clone_url}"

def discover_repositories_github():
    # Set base url
    devops_base_url = 'github.com'
    if devops_base_url_override:
        devops_base_url = devops_base_url_override
    # Get repositories
    page_size = 100
    page_num = 1
    repo_info_arr = []
    while page_num != -1:
        url = f'{http_protocol}://api.{devops_base_url}/orgs/{organization}/repos?per_page={page_size}&page={page_num}'
        print(f'GET {url}')
        get_repositories_response = requests.get(url, auth=('', access_token))
        if get_repositories_response.status_code != 200:
            print(f'Error: Unable to retrieve repositories from Github. Status code: {get_repositories_response.status_code}, Reason: {get_repositories_response.reason}')
            exit(-1)
        get_projects_results = get_repositories_response.json()
        for repo in get_projects_results:
            clone_url = inject_access_token_into_clone_url("oauth2",repo["clone_url"], access_token)
            default_branch = ""
            if "default_branch" in repo:
                default_branch = repo["default_branch"]
            repo_info_arr.append(RepoInfo(organization, "", repo["name"], default_branch, clone_url).to_dict())
        
        # paginate
        link = get_repositories_response.headers.get('Link')
        print(link)
        if not link or not (link.__contains__("rel=\"next\"")):
            page_num = -1
        else: 
            page_num = page_num + 1
    return repo_info_arr

def discover_repositories_azure_dev_ops():
    # Set base url
    devops_base_url = 'dev.azure.com'
    if devops_base_url_override:
        devops_base_url = devops_base_url_override
    
    # Initialize variables
    repo_info_arr = []
    continuation_token = None

    while True:
        # Construct the URL with the continuation token if it exists
        url = f'{http_protocol}://{devops_base_url}/{organization}/_apis/git/repositories?api-version=7.1'
        if continuation_token:
            url += f'&continuationToken={continuation_token}'
        
        print(f'GET {url}')
        get_repositories_response = requests.get(url, auth=('', access_token))
        if get_repositories_response.status_code != 200:
            print(f'Error: Unable to retrieve repositories from Azure DevOps. Status code: {get_repositories_response.status_code}, Reason: {get_repositories_response.reason}')
            exit(-1)
        get_repositories_results = get_repositories_response.json()
        repo_info_arr = []
        for repo in get_repositories_results["value"]:
            default_branch = ""
            if "defaultBranch" in repo:
                default_branch = repo["defaultBranch"]
            clone_url = inject_access_token_into_clone_url("oauth2",repo["webUrl"], access_token)
            project_name = ""
            if "project" in repo:
                project_name = repo["project"]["name"]
            # Get the repo name from the clone url in case of spaces
            repo_name = repo["webUrl"].split("/_git/")[1]
            repo_info_arr.append(RepoInfo(organization, project_name, repo_name, default_branch, clone_url).to_dict())
        # Check for continuation token
        continuation_token = get_repositories_results.get('continuationToken')
        if not continuation_token:
            break
    return repo_info_arr

def discover_repositories_gitlab():
    # Set base url
    devops_base_url = 'gitlab.com'
    if devops_base_url_override:
        devops_base_url = devops_base_url_override
    # Get repositories
    url = f'{http_protocol}://{access_token}@{devops_base_url}/api/v4/groups/{organization}/projects?per_page=100&page=1'
    print(f'GET {url}')
    get_repositories_response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
    if get_repositories_response.status_code != 200:
        print(f'Error: Unable to retrieve repositories from Gitlab. Status code: {get_repositories_response.status_code}, Reason: {get_repositories_response.reason}')
        exit(-1)
    get_projects_results = get_repositories_response.json()
    repo_info_arr = []
    for repo in get_projects_results:
        clone_url = inject_access_token_into_clone_url("oauth2",repo["http_url_to_repo"],access_token)
        default_branch = ""
        if "default_branch" in repo:
            default_branch = repo["default_branch"]
        repo_info_arr.append(RepoInfo(organization, "", repo["path"], default_branch, clone_url).to_dict())
    return repo_info_arr

def discover_repositories_bitbucket():
    """
    URL to get repositories from Bitbucket will look like this: \n
    https://api.bitbucket.org/2.0/repositories/organization?pagelen=100&page=1
    """
    # Set base url
    devops_base_url = 'bitbucket.org'
    if devops_base_url_override:
        devops_base_url = devops_base_url_override
    # Get repositories
    url = f'{http_protocol}://api.{devops_base_url}/2.0/repositories/{organization}?pagelen=100&page=1'
    print(f'GET {url}')
    get_repositories_response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
    if get_repositories_response.status_code != 200:
        print(f'Error: Unable to retrieve repositories from Bitbucket. Status code: {get_repositories_response.status_code}, Reason: {get_repositories_response.reason}')
        exit(-1)
    get_projects_results = get_repositories_response.json()
    print(json.dumps(get_projects_results, indent=4))
    repo_info_arr = []
    for repo in get_projects_results["values"]:
        # set default branch
        default_branch = ""
        if "mainbranch" in repo:
            default_branch = repo["mainbranch"]["name"]
        # set project info
        project_name = ""
        if "project" in repo:
            project_name = repo["project"]["name"]
        clone_url = ""
        for link in repo["links"]["clone"]:
            if link["name"] == "https":
                clone_url = inject_access_token_into_clone_url("x-token-auth",link["href"].split("@")[1], access_token)
        print(f"Clone URL: {clone_url}")
        repo_info_arr.append(RepoInfo(organization, project_name, repo["slug"], default_branch, clone_url).to_dict())
    return repo_info_arr

# Needed for Windows to delete git object files
def make_writable_and_delete(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delete_folder(folder_path):
    absolute_path = os.path.abspath(folder_path)
    if os.path.exists(absolute_path):
        shutil.rmtree(absolute_path, onerror=make_writable_and_delete)
    else:
        print(f"The folder {absolute_path} does not exist.")

repo_info_arr = []
if devops == 'GitLab':
    repo_info_arr = discover_repositories_gitlab()
    print(json.dumps(repo_info_arr, indent=4))
elif devops == 'GitHub':
    repo_info_arr = discover_repositories_github()
    print(json.dumps(repo_info_arr, indent=4))
elif devops == 'AzureDevOps':
    repo_info_arr = discover_repositories_azure_dev_ops()
    print(json.dumps(repo_info_arr, indent=4))
elif devops == 'Bitbucket':
    repo_info_arr = discover_repositories_bitbucket()
    print(json.dumps(repo_info_arr, indent=4))

repo_report_file_names=""
failed_repos = []
success_repos = []
total_repos_count=len(repo_info_arr)
command_strings = []
path_to_output_directory = "output"
path_to_commands_file = "commands.txt"
# Now, loop through the stored rows
for index, repo_info in enumerate(repo_info_arr, start=1):  # Adding an index starting from 1
    # pull out all relevant information from the repo_info object all at once
    repo_id = repo_info["id"]
    repo_name = repo_info["repository_name"]
    clone_url = repo_info["clone_url"]
    project_name = repo_info["project_name"]
    default_branch = repo_info["default_branch"]
    organization_name = repo_info["organization_name"]

    repo_report_file_name = f"{repo_id}.txt"
    repo_report_by_file_file_name = f"{repo_id}-by-file.txt"

    print(f"Processing repo {index}/{total_repos_count}: {repo_name} - repo_id: {repo_id}")
    # Clone repo
    command_full_string = f"git clone --depth=1 {clone_url} --single-branch"
    print(command_full_string)
    command_strings.append(command_full_string)
    exit_code = os.system(command_full_string)
    if (exit_code != 0):
        exit(exit_code)
    print(f"Successfully cloned {clone_url}")
    # Run cloc
    repo_report_file_name_path = os.path.join(path_to_output_directory, repo_report_file_name)
    # example: cloc --report-file=repo_id.txt repo_id
    command_full_string = f"{path_to_cloc} --report-file={repo_report_file_name_path} {repo_name}"
    print(command_full_string)
    command_strings.append(command_full_string)
    exit_code = os.system(command_full_string)
    if (exit_code != 0):
        exit(exit_code)
    # Run cloc by file
    repo_report_by_file_file_name_path = os.path.join(path_to_output_directory, repo_report_by_file_file_name)
    # example: cloc --report-file=repo_id-by-file.txt --by-file repo_id
    command_full_string = f"{path_to_cloc} --report-file={repo_report_by_file_file_name_path} --by-file {repo_name}"
    print(command_full_string)
    command_strings.append(command_full_string)
    exit_code = os.system(command_full_string)
    if (exit_code != 0):
        exit(exit_code)
    # Delete folder
    delete_folder(repo_name)
    # Add report file name to list
    repo_report_file_names += f"{repo_report_file_name_path} "
    success_repos.append(repo_id)
    
failed_repos_count = len(failed_repos)
success_repos_count = len(success_repos)
total_repos_count = failed_repos_count + success_repos_count

print("RESULTS:")
print("Sucessful repos:")
print(success_repos)
print("Failed repos:")
print(failed_repos)

print("Summarizing reports...")
if (success_repos_count > 0):   
    # Summarize reports using cloc
    # example cloc --sum-reports repo_id.txt repo_id2.txt
    command_full_string = f"{path_to_cloc} --sum-report {repo_report_file_names}"
    print(command_full_string)
    command_strings.append(command_full_string)
    exit_code = os.system(command_full_string)
    if (exit_code != 0):
        exit(exit_code)

print(f"Complete! Successfully cloned and ran cloc for {success_repos_count} / {total_repos_count} repositories. See logs above for more details.")

# Write out the commands that were run to a file
if (len(command_strings) > 0):
    with open(f"{path_to_commands_file}", "w") as f:
        for command in command_strings:
            f.write(f"{command}\n")
    print(f"Commands that were run are written to {path_to_commands_file}")