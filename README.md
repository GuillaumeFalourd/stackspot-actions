[![Vulnerability Check](https://github.com/GuillaumeFalourd/stackspot-actions/actions/workflows/vulnerability-check.yaml/badge.svg)](https://github.com/GuillaumeFalourd/stackspot-actions/actions/workflows/vulnerability-check.yaml) [![Container Check](https://github.com/GuillaumeFalourd/stackspot-actions/actions/workflows/container-check.yaml/badge.svg)](https://github.com/GuillaumeFalourd/stackspot-actions/actions/workflows/container-check.yaml)

# stackspot-actions

Repository with StackSpot actions

## Actions

### Ready

`stk run action crontainer-check`: Action to check container image vulnerabilities

`stk run action create-github-repo`: Action to create a GitHub repository

`stk run action delete-github-repo`: Action to delete a GitHub repository

`stk run action create-github-release`: Action to create a GitHub repository release

`stk run action vulnerability-check`: Action using StackSpot AI remote quick command to check folder files vulnerabilities.

### On Going

`stk run action create-github-secret`: Action to create a GitHub repository secret

`stk run action owasp-check`: Action using StackSpot AI remote quick command to check files vulnerabilities focussing on OWASP top 10. 

`stk run action dynamodb-backup`: Action to create a AWS Dynamo DB backup

## Example

When running the `stk run action vulnerability-check` locally, it's possible to check all files vulnerabilities in the current and sub-directories.

<img width="1003" alt="Screenshot 2024-04-25 at 09 25 27" src="https://github.com/GuillaumeFalourd/stackspot-actions/assets/22433243/9815cfd6-272f-4589-ba68-7cfa1b726593">

When running the `stk run action container-check` locally, itś possible to check all Dockerfile image vulnerabilities in the current and sub-directories.

![Captura de tela de 2024-12-04 10-17-31](https://github.com/user-attachments/assets/721c3bae-51e6-4064-9f72-ba9c49143ecf)
