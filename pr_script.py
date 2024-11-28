import os
import csv
import subprocess
import requests
from datetime import datetime

# Function to execute shell commands
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)
    return result.stdout.strip()

# Function to create a pull request using GitHub API
def create_pull_request(repo_owner, repo_name, branch_name, token, test_number):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "title": f"Fix Dockerfile vulnerabilities {test_number}",
        "body": "An automated PR which updates Docker base images to address vulnerabilities using StackSpot.",
        "head": branch_name,
        "base": "main"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error creating pull request: {response.status_code} {response.text}")
        exit(1)

# Main script
def main():
    # Check if there are changes in the repository
    changes = run_command("git status --porcelain")
    if not changes:
        print("WARNING: No changes were detected.")
        return

    # Get repository name and owner from environment variables
    github_repository = os.getenv("GITHUB_REPOSITORY")
    if not github_repository:
        print("Error: GITHUB_REPOSITORY environment variable is not set.")
        exit(1)
    repo_owner, repo_name = github_repository.split("/")

    # Generate branch name
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"stackspot-{repo_name}-{timestamp}"

    # Configure Git user
    run_command('git config --global user.name "stackspot[bot]"')
    run_command('git config --global user.email "stackspot[bot]@users.noreply.github.com"')

    # Create a new branch, add changes, commit, and push
    run_command(f"git checkout -b {branch_name}")
    run_command("git add .")
    run_command('git commit -m "Update Dockerfile base image to fix vulnerabilities using StackSpot."')
    run_command(f"git push origin {branch_name}")

    # Get GitHub token from environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        exit(1)

    # Create a pull request
    test_number = os.getenv("TEST_NUMBER")
    print(f"Test number: '{test_number}'.")
    pr_response = create_pull_request(repo_owner, repo_name, branch_name, github_token, test_number)

    # Extract PR URL and number of files updated
    pr_url = pr_response["html_url"]
    print(f"PR URL: '{pr_url}'.")
    files_updated = pr_response["changed_files"]
    print(f"Updated files: '{files_updated}'.")

    # Fill CSV file name
    github_workspace = os.getenv("GITHUB_WORKSPACE") 
    path_file = os.getenv("PATH_FILE") 
    csv_file = github_workspace + "/" + path_file
    print(f"CSV file: '{csv_file}'.")

    # Append data to the CSV file
    with open(csv_file, "a") as file:
        file.write(f"{test_number},{pr_url},{files_updated}\n")

    print(f"CSV file '{csv_file}' updated successfully.")

    # Open and read the CSV file
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        
        # Iterate through each row in the CSV file
        for row in reader:
            print(row)
    
    # Check if there are changes in the repository
    changes = run_command("git status --porcelain")
    if not changes:
        print("WARNING: No changes were detected")
        return

    # Update CSV file on main branch
    run_command(f"git checkout main")
    run_command("git clean -fd")  # Forcefully remove untracked files and directories
    run_command("git pull origin main")  # Pull the latest changes from the remote main branch
    run_command(f"git add .")
    run_command(f'git commit -m "Update {path_file} on main branch."')
    run_command(f"git push origin main")

if __name__ == "__main__":
    main()