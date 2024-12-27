import boto3
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


def create_dynamodb_backup(dynamodb_client, table_name):
    """
    Creates an on-demand backup for the specified DynamoDB table.
    """
    try:
        backup_name = f"{table_name}-backup-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        response = dynamodb_client.create_backup(TableName=table_name, BackupName=backup_name)
        backup_details = response['BackupDetails']
        print(f"Backup created successfully: {backup_details}")
        return backup_details
    except ClientError as e:
        print(f"Error: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def list_dynamodb_backups(dynamodb_client, table_name):
    """
    Lists all available backups for the specified DynamoDB table.
    """
    try:
        response = dynamodb_client.list_backups(TableName=table_name)
        backups = response.get('BackupSummaries', [])
        if backups:
            print(f"Available backups for table '{table_name}':")
            for backup in backups:
                print(
                    f"- BackupName: {backup['BackupName']}, "
                    f"BackupArn: {backup['BackupArn']}, "
                    f"BackupStatus: {backup['BackupStatus']}, "
                    f"BackupCreationDateTime: {backup['BackupCreationDateTime']}"
                )
        else:
            print(f"No backups found for table '{table_name}'.")
        return backups
    except ClientError as e:
        print(f"Error: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def run(metadata):
    """
    Main function to execute the backup and list operations.
    """
    try:
        inputs = metadata.inputs
        table_name = inputs.get("dynamodb_table_name", "").strip()
        aws_access_key_id = inputs.get("aws_access_key_id", "").strip()
        aws_secret_access_key = inputs.get("aws_secret_access_key", "").strip()
        aws_region = inputs.get("aws_region", "").strip()

        if not all([table_name, aws_access_key_id, aws_secret_access_key, aws_region]):
            raise ValueError("All input fields (table name, AWS credentials, and region) are required.")

        # Initialize DynamoDB client
        dynamodb_client = initialize_dynamodb_client(aws_access_key_id, aws_secret_access_key, aws_region)

        # Create a backup
        print("Creating a backup...")
        create_dynamodb_backup(dynamodb_client, table_name)

        # List available backups
        print("\nListing available backups...")
        list_dynamodb_backups(dynamodb_client, table_name)

    except (NoCredentialsError, PartialCredentialsError):
        print("Error: Invalid or missing AWS credentials.")
    except ValueError as e:
        print(f"Input Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")