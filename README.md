# Sonar Lines of Code (LOC) Count Tool

## Overview

The Sonar LOC Count Tool simplifies the process of obtaining an accurate Lines of Code (LOC) count for an organization's DevOps platform. This tool can automatically discover repositories and calculate the total LOC, with just two Python scripts.

```
-------------------------------------------------------------------------------
File                         files          blank        comment           code
-------------------------------------------------------------------------------
repo3.txt                        2             13              4             73
repo1.txt                        3             10              4             49
repo2.txt                        1              4              0             16
-------------------------------------------------------------------------------
SUM:                             6             27              8            138
-------------------------------------------------------------------------------
Complete! Successfully cloned and ran cloc for 3 / 3 repositories. See logs above for more details.
```

## Requirements
1. **Recommended**: use the provided Dockerfile for containerization, encapsulating all necessary dependencies and simplifying setup and execution. Simply clone this repository, build, and run the docker container. Instructions can be found [here](#docker). If you plan to run from your local machine and not within the Docker container, please refer to the [prerequisites](#local).

2. An **Access Token** for the appropriate DevOps platform (GitHub, Azure DevOps, GitLab, or Bitbucket) will be required. This token will need **read** access each of the repositories in order to discover and clone the repositories.

## Usage

#### Step 1: Discovering Respositories within an Organization

This initial step leverages the APIs of major DevOps platforms (GitHub, Azure DevOps, GitLab, and Bitbucket) to identify all repositories within an organization. The results are saved to a CSV file, which includes a specially constructed URL for each repository, complete with an authentication token for `git clone` operations in Step 2.

To perform this step from within the Docker container, run the appropriate script for your DevOps platform, replacing `<YourOrganizationName>`, `<YourPersonalAccessToken>`, and `<PathToOutputCsv>` with your organization name, personal access token, and desired path for the output CSV, respectively.

- **GitHub**:
    ```sh
    python3 github-discover-repos.py  --organization <YourOrganizationName>  --connectionToken <YourPersonalAccessToken>  --outputCsv <PathToOutputCsv>
    ```
- **Azure DevOps**:
    ```sh
    python3 azure-devops-discover-repos.py  --organization <YourOrganizationName>  --connectionToken <YourPersonalAccessToken>  --outputCsv <PathToOutputCsv>
    ```
- **GitLab**:
    ```sh
    python3 gitlab-discover-repos.py  --organization <YourOrganizationName>  --connectionToken <YourPersonalAccessToken>  --outputCsv <PathToOutputCsv>
    ```
- **Bitbucket**:
    ```sh
    python3 bitbucket-discover-repos.py  --organization <YourOrganizationName>  --connectionToken <YourPersonalAccessToken>  --outputCsv <PathToOutputCsv>
    ```

#### Step 2: Calculating Lines of Code

Following repository discovery, the tool clones each repository using the URLs from the CSV file created in Step 1 and employs `cloc` to calculate the LOC. This process is automated and culminates in a comprehensive report detailing the total LOC across the organization's codebase.

To perform this step, run:

```sh
python3 cloc.py --inputCsv <PathToInputCsv> --outputDir <PathToOutputDirectory>
```

This will clone each repository, run `cloc` to count lines of code, and output the results to the specified directory.

The output directory will contain 2 reports for each of the repositories that were counted. The first will count the lines of code by programming language and the second will count the lines of code by file. The final step of this python script will sum up the total lines of code for all of the repositories combined by running the `cloc --sum-reports` command. If you would like to adjust this particular results or run the cloc tool again. Please refer to the cloc manual by running `cloc --help`. 

## Appendix

### Building and Running a Docker Container #docker

To build a Docker container from a Dockerfile in the current directory, run the following command:

```sh
# Build the docker container locally
docker build -t your-image-name .

# Run the docker container
docker run -d --name your-container-name your-image-name

# Connect to the container
docker exec -it your-container-name /bin/sh
```

Once the Docker container is up and running, follow the steps below to discover repositories and calculate lines of code using the provided scripts.

### Requirements (If Not Using Docker) #local
If you plan to run the python scripts on your local machine without using Docker, please ensure the following dependencies are installed on your system:

- **cloc**: A tool for counting lines of code. [Installation Guide](https://github.com/AlDanial/cloc)
- **Python3**
- **Python modules**:
   - `requests`: For making API calls to DevOps platforms.
   - `csv`: For handling CSV file operations.
   - `argparse`: For parsing command-line options and arguments.
   - `subprocess`: For executing external commands (e.g., `git clone` and `cloc`).
   - `os`: For directory operations.
   - `shutil`: For file and directory operations, including deletion.

### Important Commands
Below are the important CLI commands that are run during these operations:

```sh
# Clone the repository
git clone <url_with_access_token> --single-branch

# This cloc report is for a single repository and can be combined later for a total summation
cloc --report-file=<repo_report_file_name> <path_to_repository>

# This cloc report combines previous single repository reports into a total report
cloc --sum-reports <repo_report_file_name1> <repo_report_file_name2> ...

# Optional repository analysis breakdown by file
# Note that this report cannot be used in the summation report
cloc --report-file=<repo_report_file_name> <path_to_repository> --by-file
```