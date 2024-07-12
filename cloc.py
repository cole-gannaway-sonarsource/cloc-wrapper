import csv
import subprocess
import os
import shutil
import argparse

parser = argparse.ArgumentParser(description='Script to run cloc against repositories in a csv.')

# Add arguments
parser.add_argument('--inputCsv', type=str, help='Input csv containing the repo id, repo name, and git clone url with authentication token', required=True)
parser.add_argument('--outputDir', type=str, help='Output folder that you want to dump the cloc reports to. Make sure not to add a trailing slash', required=True)

# Parse the arguments
args = parser.parse_args()

path_to_input_csv = args.inputCsv
path_to_output_directory = args.outputDir

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

repo_report_file_names=""
failed_repos = []
with open(f"{path_to_input_csv}", mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        repo_id, repo, repo_url = row
        repo_report_file_name = f"{repo_id}.txt"
        repo_report_by_file_file_name = f"{repo_id}-by-file.txt"
        # Clone repo
        try:
            print(f"git clone {repo_url}")
            subprocess.run(["git", "clone", repo_url, "--single-branch"], check=True)
            print(f"Successfully cloned {repo_url}")
            # Run cloc
            print(f"cloc --report-file={path_to_output_directory}/{repo_report_file_name} {repo}")
            subprocess.run(["cloc", f"--report-file={path_to_output_directory}/{repo_report_file_name}", f"{repo}"], check=True)
            # Run cloc by file
            print(f"cloc --report-file={path_to_output_directory}/{repo_report_by_file_file_name} {repo}")
            subprocess.run(["cloc", f"--report-file={path_to_output_directory}/{repo_report_by_file_file_name}", "--by-file", f"{repo}"], check=True)
            # Delete repo
            delete_folder(f"{repo}")
            # Add report file name to list
            repo_report_file_names += f"{path_to_output_directory}/{repo_report_file_name} "
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone {repo_url}. Error: {e}")
            failed_repos.append(repo)

# Summarize reports using cloc
print(f"cloc --sum-report {repo_report_file_names}")
subprocess.run(["cloc", "--sum-reports"] + repo_report_file_names.split(), check=True)

# Print failed repos
if (len(failed_repos) > 0):
    print(f"Failed to clone the following repos: {failed_repos}")