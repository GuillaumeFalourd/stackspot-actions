#!/usr/bin/python3
import requests
import json


def run(metadata):
    inputs = metadata.inputs
    token = inputs.get("stk_github_token")
    repository = inputs.get("stk_github_repository")
    description = inputs.get("stk_github_description")
    branch = inputs.get("stk_github_branch")
    version = inputs.get("stk_github_version")

    authorization = f"token {token}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization" : authorization,
        "X-GitHub-Api-Version": "2022-11-28",
        }

    url_user = "https://api.github.com/user"

    r1 = requests.get(
        url=url_user,
        headers=headers,
        verify=False,
        )

    if r1.status_code == 200:

        owner = json.loads(r1.content)["login"]

        github_api_url = f"https://api.github.com/repos/{owner}/{repository}/releases"

        data = {}
        data["body"] = description
        data["target_commitish"] = branch
        data["tag_name"] = version
        data["name"] = f"Release {version}"
        json_data = json.dumps(data)

        r2 = requests.post(
            url=github_api_url,
            data = json_data,
            headers=headers,
            verify=False,
            )
        
        if r2.status_code == 201:
            print(f"✅ Release \033[36m{version}\033[0m successfully generated for {owner}'s \033[36m{repository}\033[0m repository")
        
        else:
            print("❌ Couldn't generate repository release")
            print (r2.status_code, r2.reason)

    else:
        print(f"❌ Couldn't identify owner from informed Token")
        print (r1.status_code, r1.reason)
