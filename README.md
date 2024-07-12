# Sonar Lines of Code (LOC) Count Tool

## Overview

The Sonar LOC Count Tool simplifies the process of obtaining an accurate Lines of Code (LOC) count across all repositories within an organization's DevOps platform. Designed for efficiency and ease of use, this tool automates the discovery of repositories and the calculation of total LOC, streamlining the assessment of your organization's codebase size with just two scripts.

## Requirements

Before using this tool, ensure the following dependencies are installed on your system:

- **cloc**: A tool for counting lines of code. [Installation Guide](https://github.com/AlDanial/cloc)
- **python - modules listed below**:
  - `requests`: For making API calls to DevOps platforms.
  - `csv`: For handling CSV file operations.
  - `argparse`: For parsing command-line options and arguments.
  - `subprocess`: For executing external commands (e.g., `git clone` and `cloc`).
  - `os`: For directory operations.
  - `shutil`: For file and directory operations, including deletion.

This project includes a Dockerfile for containerization, encapsulating all necessary dependencies and simplifying setup and execution.

Additionally, an **Access Token** for the appropriate DevOps platform (GitHub, Azure DevOps, GitLab, or Bitbucket) will be required. This token is necessary to clone repositories and run `cloc` against them, ensuring secure and authorized access to your organization's codebase.

## Getting Started

### Initial Setup

1. Clone this repository to your local machine.
2. Proceed with the two-step process outlined below to discover repositories and calculate the LOC for each.

*Optional*: Utilize the provided Dockerfile for an encapsulated environment, ensuring a consistent setup across different systems.

### Usage Guide

#### Step 1: Discovering Repositories

This initial step leverages the APIs of major DevOps platforms (GitHub, Azure DevOps, GitLab, and Bitbucket) to identify all repositories within an organization. The results are saved to a CSV file, which includes a specially constructed URL for each repository, complete with an authentication token for `git clone` operations.

To perform this step, run the appropriate script for your DevOps platform from within the Docker container. Replace `<YourOrganizationName>`, `<YourPersonalAccessToken>`, and `<PathToOutputCsv>` with your organization name, personal access token, and desired path for the output CSV, respectively.

Note: please ensure that the access token has "read repository" access for all repositories that you are planning to count LOC for. The following script will 'git clone' each repository.

- **GitHub**:
    ```sh
    python3 github-discover-repos.py --organization <YourOrganizationName> --connectionToken <YourPersonalAccessToken> --outputCsv <PathToOutputCsv>
    ```
- **Azure DevOps**:
    ```sh
    python3 azure-devops-discover-repos.py --organization <YourOrganizationName> --connectionToken <YourPersonalAccessToken> --outputCsv <PathToOutputCsv>
    ```
- **GitLab**:
    ```sh
    python3 gitlab-discover-repos.py --organization <YourOrganizationName> --connectionToken <YourPersonalAccessToken> --outputCsv <PathToOutputCsv>
    ```
- **Bitbucket**:
    ```sh
    python3 bitbucket-discover-repos.py --organization <YourOrganizationName> --connectionToken <YourPersonalAccessToken> --outputCsv <PathToOutputCsv>
    ```

#### Step 2: Calculating Lines of Code

Following repository discovery, the tool clones each repository using the URLs from the CSV file in Step 1 and employs `cloc` to calculate the LOC. This process is automated and culminates in a comprehensive report detailing the total LOC across the organization's codebase.

To perform this step, run:

```sh
python3 cloc.py --inputCsv <PathToInputCsv> --outputDir <PathToOutputDirectory>
```

This will clone each repository, run `cloc` to count lines of code, and output the results to the specified directory.

The output directory will contain 2 reports for each of the repositories that were counted. The first will count the lines of code by language and the sencond will count the lines of code by file. The final step of this python script will sum up the total lines of code for all of the repositories combined by running the cloc --sum all report. If you would like to adjust this particular results or run the cloc tool again. Please refere to the cloc manual by running cloc --help. Below are the main commands that are executed during cloc.py .

```sh
# Clone the repository
git clone <url_with_access_token> --single-branch
# Run CLOC with standard output by language to ensure summation of reports work
cloc --report-file=<repo_report_file_name> <path_to_repository>
# Combine previous reports
cloc --sum-reports <repo_report_file_name1> <repo_report_file_name2> ...


# Optional repository analysis break down by file
# Note that this report can not be used in the summation report
cloc --report-file=<repo_report_file_name> <path_to_repository> --by-file
```

## Building and Running a Docker Container

To build a Docker container from a Dockerfile in the current directory, run the following command:

```sh
# Build the docker container locally
docker build -t your-image-name .

# Run the docker container
docker run -d --name your-container-name your-image-name

# Connect to the container
docker exec -it your-container-name /bin/sh
```