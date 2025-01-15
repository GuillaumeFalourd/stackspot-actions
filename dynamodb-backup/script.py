import boto3
import time
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from datetime import datetime


def initialize_dynamodb_client(aws_access_key_id, aws_secret_access_key, aws_region):
    """
    Initializes and returns a DynamoDB client.
    """
    return boto3.client(
        'dynamodb',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )


def initialize_s3_client(aws_access_key_id, aws_secret_access_key, aws_region):
    """
    Initializes and returns an S3 client.
    """
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )


def export_dynamodb_table_to_s3(dynamodb_client, table_name, s3_bucket_name, s3_prefix):
    """
    Exports a DynamoDB table to an S3 bucket.
    """
    try:
        # Start the export task for the DynamoDB table
        export_task = dynamodb_client.export_table_to_point_in_time(
            TableArn=f"arn:aws:dynamodb:{boto3.session.Session().region_name}:{boto3.client('sts').get_caller_identity()['Account']}:table/{table_name}",
            S3Bucket=s3_bucket_name,
            S3Prefix=s3_prefix,
            ExportFormat='DYNAMODB_JSON'
        )
        export_task_id = export_task['ExportDescription']['ExportArn']
        print(f"Export task started with ID: {export_task_id}")

        # Wait for the export task to complete
        print("Waiting for the export task to complete...")
        while True:
            export_status = dynamodb_client.describe_export(ExportArn=export_task_id)
            status = export_status['ExportDescription']['ExportStatus']
            if status == 'COMPLETED':
                print("Export task completed successfully.")
                break
            elif status == 'FAILED':
                print("Export task failed.")
                return
            else:
                print(f"Export task status: {status}. Waiting...")
            time.sleep(30)

        print(f"Backup of table '{table_name}' saved to S3 bucket '{s3_bucket_name}' with prefix '{s3_prefix}'.")
    except ClientError as e:
        print(f"An error occurred: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def run(metadata):
    """
    Main function to execute the backup operation.
    """
    try:
        inputs = metadata.inputs
        table_name = inputs.get("dynamodb_table_name", "").strip()
        s3_bucket_name = inputs.get("s3_bucket_name", "").strip()
        aws_access_key_id = inputs.get("aws_access_key_id", "").strip()
        aws_secret_access_key = inputs.get("aws_secret_access_key", "").strip()
        aws_region = inputs.get("aws_region", "").strip()

        # Hardcoded S3 prefix
        s3_prefix = "backups/dynamodb/"

        if not all([table_name, s3_bucket_name, aws_access_key_id, aws_secret_access_key, aws_region]):
            raise ValueError("All input fields (table name, S3 bucket name, AWS credentials, and region) are required.")

        # Initialize DynamoDB and S3 clients
        dynamodb_client = initialize_dynamodb_client(aws_access_key_id, aws_secret_access_key, aws_region)
        s3_client = initialize_s3_client(aws_access_key_id, aws_secret_access_key, aws_region)

        # Check if the S3 bucket exists
        try:
            s3_client.head_bucket(Bucket=s3_bucket_name)
            print(f"S3 bucket '{s3_bucket_name}' exists.")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"S3 bucket '{s3_bucket_name}' does not exist.")
                return
            else:
                raise

        # Export the DynamoDB table to S3
        print("Exporting DynamoDB table to S3...")
        export_dynamodb_table_to_s3(dynamodb_client, table_name, s3_bucket_name, s3_prefix)

    except (NoCredentialsError, PartialCredentialsError):
        print("Error: Invalid or missing AWS credentials.")
    except ValueError as e:
        print(f"Input Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")