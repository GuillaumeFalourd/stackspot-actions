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

When running the `stk run action container-check` locally, itś possible to check all Dockerfile image vulnerabilities in the current and sub-directories.