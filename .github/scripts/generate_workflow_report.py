import os
import requests
import pandas as pd
from datetime import datetime

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

# Get environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

# Headers for GitHub API requests
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_workflows():
    """Fetch all workflows in the repository."""
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["workflows"]

def fetch_workflow_runs(workflow_id):
    """Fetch all runs for a specific workflow."""
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{workflow_id}/runs"
    runs = []
    page = 1

    while True:
        response = requests.get(f"{url}?per_page=100&page={page}", headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        runs.extend(data["workflow_runs"])
        if "next" not in response.links:
            break
        page += 1

    return runs

def process_workflow_data(workflows):
    """Process workflow data to generate the report."""
    report_data = []

    for workflow in workflows:
        workflow_id = workflow["id"]
        workflow_name = workflow["name"]
        runs = fetch_workflow_runs(workflow_id)

        total_runs = len(runs)
        successful_runs = [run for run in runs if run["conclusion"] == "success"]
        success_rate = (len(successful_runs) / total_runs) * 100 if total_runs > 0 else 0

        successful_durations = [
            (datetime.strptime(run["updated_at"], "%Y-%m-%dT%H:%M:%SZ") -
             datetime.strptime(run["run_started_at"], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
            for run in successful_runs
        ]
        avg_successful_duration = sum(successful_durations) / len(successful_durations) if successful_durations else 0

        report_data.append({
            "Workflow Name": workflow_name,
            "Total Executions": total_runs,
            "Successful Executions (%)": round(success_rate, 2),
            "Average Successful Execution Time (s)": round(avg_successful_duration, 2)
        })

    return report_data

def save_report(report_data):
    """Save the report as a CSV file."""
    df = pd.DataFrame(report_data)
    df.to_csv("workflow_execution_report.csv", index=False)

def main():
    print("Fetching workflows...")
    workflows = fetch_workflows()

    print("Processing workflow data...")
    report_data = process_workflow_data(workflows)

    print("Saving report...")
    save_report(report_data)

    print("Report generated: workflow_execution_report.csv")

if __name__ == "__main__":
    main()