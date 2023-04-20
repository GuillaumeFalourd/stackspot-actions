#!/usr/bin/python3
import requests
import json
import re
import os

def run(metadata):
    inputs = metadata.inputs
    token = inputs.get("stk_github_token")
    repository = inputs.get("stk_github_repository")
    private = inputs.get("stk_github_private")

    repository = urlify(repository)

    url_user = "https://api.github.com/user"
    url_repos = f"https://api.github.com/user/repos"

    data = {}
    data["name"] = repository
    data["description"] = "Project created with StackSpot"
    data["homepage"] = "https://v1.stackspot.com"
    data["auto_init"] = True
    if private == "No":
        data["private"] = False
    else:
        data["private"] = True

    json_data = json.dumps(data)

    authorization = f"token {token}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization" : authorization,
        "X-GitHub-Api-Version": "2022-11-28",
        }
    
    r = requests.get(
        url=url_user,
        headers=headers,
        verify=False,
        )

    if r.status_code == 200:

        owner = json.loads(r.content)["login"]

        r = requests.post(
            url=url_repos,
            data=json_data,
            headers=headers,
            verify=False,
            )

        if r.status_code == 201:
            print(f"✅ Repository successfully created on \033[36mhttps://github.com/{owner}/{repository}\033[0m!")

        else:
            print(f"❌ Couldn't create {owner}'s new repository")
            print (r.status_code, r.reason)

    else:
        print(f"❌ Couldn't identify owner from informed Token")
        print (r.status_code, r.reason)


def urlify(s):
    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s\-]", '', s)
    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '-', s)
    return s
