#!/usr/bin/python3
import requests
import questionary
import json
import re

def run(metadata):

    inputs = metadata.inputs
    token = inputs.get("stk_github_token")
    repository = inputs.get("stk_github_repository")

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

        if repository is None or repository == "":

            url_repos = f"https://api.github.com/user/repos?type=owner&per_page=200&sort=full_name"

            r2 = requests.get(
                url=url_repos,
                headers=headers,
                verify=False,
                )

            if r2.status_code == 200:
                datas = r2.json()
                repositories = []

                for d in datas:
                    repositories.append(d["name"])

                repository = questionary.select(
                            message = f"\033[1m\033[36m{owner}\033[0m \033[1mrepository to delete:\033[0m",
                            choices = repositories,
                        ).ask()
            
            else:
                print(f"❌ Couldn't get {owner}'s repositories")
                print(r2.status_code, r2.reason)

        else:
            url_delete = f"https://api.github.com/repos/{owner}/{repository}"

            r3 = requests.delete(
                url=url_delete,
                headers=headers,
                verify=False,
                )

            if r3.status_code == 204:
                print(f"✅ Repository \033[36mhttps://github.com/{owner}/{repository}\033[0m successfully deleted!")

            else:
                print(f"❌ Couldn't delete repository https://github.com/{owner}/{repository}")
                print(f"🚧 Please, check the token persmissions or if the repository still exists")
                print(r3.status_code, r3.reason)

    else:
        print(f"❌ Couldn't identify owner from informed Token")
        print (r1.status_code, r1.reason)
