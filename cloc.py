import csv
import subprocess
import os
import shutil
import argparse

parser = argparse.ArgumentParser(description='Script to run cloc against repositories in a csv.')

# Add arguments
parser.add_argument('--inputCsv', type=str, help='Input csv containing the repo id, repo name, and git clone url with authentication token', required=True)
parser.add_argument('--outputDir', type=str, help='Output folder that you want to dump the cloc reports to. Make sure not to add a trailing slash', required=True)
parser.add_argument('--clocPath', type=str, help="Path to cloc executable. Default is 'cloc'", required=False, default="cloc")

# Parse the arguments
args = parser.parse_args()

path_to_input_csv = args.inputCsv
path_to_output_directory = args.outputDir
path_to_cloc = args.clocPath

def create_folder(folder_path):
    try :
        os.mkdir(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_path}' already exists.")

def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' deleted successfully.")
    except Exception as e:  # Catching a more general exception since it can raise different kinds of exceptions
        print(f"Error: {e} - {folder_path}")

# Create folder to store reports
create_folder(path_to_output_directory)


# First, read in the CSV file and store rows for later processing
repos_data = []
with open(f"{path_to_input_csv}", mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        repos_data.append(row)

repo_report_file_names=""
failed_repos = []
success_repos = []
total_repos_count=len(repos_data)
# Now, loop through the stored rows
for index, row in enumerate(repos_data, start=1):  # Adding an index starting from 1
    repo_id, repo, repo_url = row
    repo_report_file_name = f"{repo_id}.txt"
    repo_report_by_file_file_name = f"{repo_id}-by-file.txt"
    print(f"Processing repo {index}/{total_repos_count}: {repo} - repo_id: {repo_id}")
    # Clone repo
    try:
        print(f"git clone {repo_url}")
        subprocess.run(["git", "clone", repo_url, "--single-branch"], check=True)
        print(f"Successfully cloned {repo_url}")
        # Run cloc
        repo_report_file_name_path = os.path.join(path_to_output_directory, repo_report_file_name)
        print(f"{path_to_cloc} --report-file={repo_report_file_name_path} {repo}")
        subprocess.run([f"{path_to_cloc}", f"--report-file={repo_report_file_name_path}", f"{repo}"], check=True)
        # Run cloc by file
        repo_report_by_file_file_name_path = os.path.join(path_to_output_directory, repo_report_by_file_file_name)
        print(f"{path_to_cloc} --report-file={repo_report_by_file_file_name_path} {repo}")
        subprocess.run([f"{path_to_cloc}", f"--report-file={repo_report_by_file_file_name_path}", "--by-file", f"{repo}"], check=True)
        # Delete repo
        delete_folder(f"{repo}")
        # Add report file name to list
        repo_report_file_names += f"{repo_report_file_name_path} "
        success_repos.append(repo_id)
    except subprocess.CalledProcessError as e:
        print(f"Failed to cloc for {repo_id} and git clone {repo_url}. Error: {e}")
        failed_repos.append(repo_id)

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
    print(f"{path_to_cloc} --sum-report {repo_report_file_names}")
    subprocess.run([f"{path_to_cloc}", "--sum-reports"] + repo_report_file_names.split(), check=True)

print(f"Complete! Successfully cloned and ran cloc for {success_repos_count} / {total_repos_count} repositories. See logs above for more details.")