import requests

DATADOG_API_KEY = "<YOUR_DATADOG_API_KEY>"
DATADOG_APP_KEY = "<YOUR_DATADOG_APP_KEY>"

def get_aws_costs(service):
    url = "https://api.datadoghq.com/api/v1/query"
    headers = {
        "Content-Type": "application/json",
        "DD-API-KEY": DATADOG_API_KEY,
        "DD-APPLICATION-KEY": DATADOG_APP_KEY,
    }
    params = {
        "query": "avg:aws.billing.estimated_charges{*}" + f"by {service}",
        "from": 1633046400,  # Start timestamp
        "to": 1633132800,    # End timestamp
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def get_kubernetes_costs(namespace):
    url = "https://api.datadoghq.com/api/v1/query"
    headers = {
        "Content-Type": "application/json",
        "DD-API-KEY": DATADOG_API_KEY,
        "DD-APPLICATION-KEY": DATADOG_APP_KEY,
    }
    params = {
        "query": "avg:kubernetes.cpu.usage.total{*}" + f" by {namespace}",
        "from": 1633046400,  # Start timestamp
        "to": 1633132800,    # End timestamp
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


# List of AWS services
aws_services = [
    "aws.ec2",        # Amazon EC2
    "aws.s3",         # Amazon S3
    "aws.rds",        # Amazon RDS
    "aws.lambda",     # Amazon Lambda
    "aws.dynamodb",   # Amazon DynamoDB
    "aws.cloudfront", # Amazon CloudFront
    "aws.eks",        # Amazon EKS
    "aws.vpc",        # Amazon VPC
    "aws.route53",    # Amazon Route 53
    "aws.kinesis"     # Amazon Kinesis
]

print("AWS COST")
# Loop through each service and call the function
for service in aws_services:
    print(f"Fetching costs for {service}...")
    aws_costs = get_aws_costs(service)
    print(f"Costs for {service}: {aws_costs}")


# List of Kubernetes namespaces
kubernetes_namespaces = [
    "namespace1",
    "namespace2",
    "namespace3"
]

print("KUBERNETES COSTS")
# Loop through each namespace and call the function
for namespace in kubernetes_namespaces:
    print(f"Fetching costs for {namespace}...")
    kubernetes_costs = get_kubernetes_costs(namespace)
    print(f"Costs for {namespace}: {kubernetes_costs}")