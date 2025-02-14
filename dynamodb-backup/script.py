import boto3
import time
import os
import requests
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

def initialize_dynamodb_client():
    """
    Initializes and returns a DynamoDB client using the default session.
    """
    print("Initializing DynamoDB client...")
    return boto3.client('dynamodb')

def get_table_arn(dynamodb_client, table_name):
    """
    Retrieves the ARN of a DynamoDB table.
    """
    try:
        print(f"Retrieving ARN for table '{table_name}'...")
        response = dynamodb_client.describe_table(TableName=table_name)
        table_arn = response['Table']['TableArn']
        print(f"Table ARN retrieved successfully: {table_arn}")
        return table_arn
    except ClientError as e:
        print(f"ClientError occurred while retrieving table ARN: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred while retrieving table ARN: {str(e)}")
        raise

def export_dynamodb_table_to_s3(dynamodb_client, table_name, s3_bucket_name, s3_prefix):
    """
    Exports a DynamoDB table to an S3 bucket.
    """
    try:
        # Retrieve the Table ARN dynamically
        table_arn = get_table_arn(dynamodb_client, table_name)

        print(f"Starting export of DynamoDB table '{table_name}' to S3 bucket '{s3_bucket_name}' with prefix '{s3_prefix}'...")
        # Start the export task for the DynamoDB table
        export_task = dynamodb_client.export_table_to_point_in_time(
            TableArn=table_arn,
            S3Bucket=s3_bucket_name,
            S3Prefix=s3_prefix,
            ExportFormat='DYNAMODB_JSON'
        )
        export_task_id = export_task['ExportDescription']['ExportArn']
        print(f"Export task started successfully. Task ID: {export_task_id}")

        # Wait for the export task to complete
        print("Waiting for the export task to complete...")
        while True:
            export_status = dynamodb_client.describe_export(ExportArn=export_task_id)
            status = export_status['ExportDescription']['ExportStatus']
            print(f"Current export task status: {status}")
            if status == 'COMPLETED':
                print("Export task completed successfully.")
                break
            elif status == 'FAILED':
                raise RuntimeError("Export task failed. Please check the AWS Management Console for more details.")
            else:
                print("Export task is still in progress. Retrying in 30 seconds...")
                time.sleep(30)

        print(f"Backup of table '{table_name}' has been successfully saved to S3 bucket '{s3_bucket_name}' with prefix '{s3_prefix}'.")
    except ClientError as e:
        print(f"ClientError occurred: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred during the export process: {str(e)}")
        raise

def get_federation_token():
    print("Getting federated token")
    request_token = os.getenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    request_url = os.getenv("ACTIONS_ID_TOKEN_REQUEST_URL")
    header = {'Authorization': f'bearer {request_token}'}
    try:
        response = requests.get(url=f"{request_url}&audience=sts.amazonaws.com", headers=header, verify=False)
        response.raise_for_status()
        return response.json().get("token")
    except Exception as e:
        print(f"Error getting federated token: {str(e)}")
        raise

def run(metadata):
    """
    Main function to execute the backup operation.
    """
    try:
        print("Extracting inputs from metadata...")
        inputs = metadata.inputs
        table_name = inputs.get("dynamodb_table_name", "").strip()
        s3_bucket_name = inputs.get("s3_bucket_name", "").strip()
        role_arn = os.getenv("ROLE_ARN")

        # Assume role with web identity
        sts_client = boto3.client('sts')
        assumed_role = sts_client.assume_role_with_web_identity(
            RoleArn=role_arn,
            RoleSessionName="AssumeRoleSession",
            WebIdentityToken=get_federation_token(),
            DurationSeconds=3600,
        )
        credentials = assumed_role['Credentials']

        # Initialize DynamoDB client with assumed role credentials
        print("Initializing AWS clients...")
        dynamodb_client = boto3.client(
            'dynamodb',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )

        # S3 prefix
        s3_prefix = "backups/dynamodb/"

        # Proceed with the export operation
        print("Proceeding with the export process...")
        export_dynamodb_table_to_s3(dynamodb_client, table_name, s3_bucket_name, s3_prefix)

    except (NoCredentialsError, PartialCredentialsError):
        print("Error: Invalid or missing AWS credentials. Please check your AWS access key and secret key.")
    except ValueError as e:
        print(f"Input Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")