# Cloc Wrapper

## Overview

This tool simplifies the process of obtaining an accurate Lines of Code (LOC) count for an organization's DevOps platform. It can automatically discover repositories and calculate the total LOC with just two Python scripts.

Simply run the first [step](#step-1-discovering-respositories-within-an-organization) to discover all repositories in your **DevOps Organization**.
```sh
python3 azure-devops-discover-repos.py  --organization <YourOrganizationName>  --connectionToken <YourPersonalAccessToken>  --outputCsv <PathToOutputCsv>
```
Then run the second [step](#step-2-calculating-lines-of-code) to count the LOC of each repository
```sh
python3 cloc.py --inputCsv <PathToInputCsv> --outputDir <PathToOutputDirectory>
```
This will output the total Lines of Code (LOC) count for the entire organization. See example below.
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
1. **Recommended**: Use the provided Dockerfile for containerization, encapsulating all necessary dependencies. Simply clone this repository, build, and run the docker container. Instructions can be found [here](#Building-and-Running-a-Docker-Container).
    - If you plan to run from your local machine and not within the Docker container, please refer to the [prerequisites](#Local-Requirements---If-Not-Using-Docker).

3. An **Access Token** for your appropriate DevOps platform (GitHub, Azure DevOps, GitLab, or Bitbucket) with **read** access for each of the repositories within the organization.

## Usage

#### Step 1: Discovering Repositories within an Organization

This initial step leverages the APIs of major DevOps platforms (GitHub, Azure DevOps, GitLab, and Bitbucket) to identify all repositories within an organization. The results are saved to a CSV file, which includes a specially constructed URL for each repository, complete with an authentication token for `git clone` operations in [Step 2](#step-2-calculating-lines-of-code).

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

Following repository discovery, the tool clones each repository using the URLs from the CSV file created in [Step 1](#step-1-discovering-respositories-within-an-organization) and employs `cloc` to calculate the LOC. This culminates in a comprehensive report detailing the total LOC across the organization's codebase.

To perform this step, run:

```sh
python3 cloc.py --inputCsv <PathToInputCsv> --outputDir <PathToOutputDirectory>
```

The output directory will contain two reports for each repository: one by programming language and one by file. If you would like to adjust the particular results, you can run the cloc tool again. Please refer to the cloc manual by running `cloc --help`. Below are some helpful [cloc commands](#important-commands).

## Appendix

### Building and Running a Docker Container

**Prerequisite**: Install [docker](https://www.docker.com/products/docker-desktop/) for your platform.

To build a Docker container from a Dockerfile in the current directory, run the following command:

```sh
# Build the docker container locally
docker build -t cloc-wrapper-image .

# Run the docker container
docker run -d --name cloc-wrapper cloc-wrapper-image

# Connect to the container
docker exec -it cloc-wrapper /bin/sh
```

Once the Docker container is up and running, follow the [steps](#Usage) to discover repositories and calculate lines of code using the provided scripts.

### Local Requirements - If Not Using Docker
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
