import requests
import time
import json
import os

def save_output(name: str, value: str):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output_file:
        print(f'{name}<<EOF', file=output_file)
        print(value, file=output_file)
        print('EOF', file=output_file)

def extract_json_from_result(result):
    """
    Extract the JSON part from the result string.
    The result string contains both an explanation and a JSON object wrapped in triple backticks.
    """
    # Find the start and end of the JSON part
    start_index = result.find("```json")
    end_index = result.find("```", start_index + 7)  # Find the closing backticks after the JSON

    if start_index != -1 and end_index != -1:
        # Extract the JSON part and strip any leading/trailing whitespace
        json_part = result[start_index + 7:end_index].strip()
        return json_part
    else:
        raise ValueError("No valid JSON found in the result string.")

# Step 1: Authentication to obtain access token
def get_access_token(account_slug, client_id, client_key):
    url = f"https://idm.stackspot.com/{account_slug}/oidc/oauth/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'client_id': client_id,
        'grant_type': 'client_credentials',
        'client_secret': client_key
    }
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()
    return response_data['access_token']

# Step 2: Creation of a Quick Command (RQC) execution
def create_rqc_execution(qc_slug, access_token, input_data):
    url = f"https://genai-code-buddy-api.stackspot.com/v1/quick-commands/create-execution/{qc_slug}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    data = {
        'input_data': input_data
    }

    # print('File data to analyze:', data) 
    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        decoded_content = response.content.decode('utf-8')  # Decode bytes to string
        extracted_value = decoded_content.strip('"')  # Strip the surrounding quotes
        response_data = extracted_value
        return response_data
    else:
        print(response.status_code)
        print(response.content)

# Step 3: Polling for the execution status
def get_execution_status(execution_id, access_token):
    url = f"https://genai-code-buddy-api.stackspot.com/v1/quick-commands/callback/{execution_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    i = 0
    while True:
        response = requests.get(
            url, 
            headers=headers
        )
        response_data = response.json()
        status = response_data['progress']['status']
        if status in ['COMPLETED', 'FAILURE']:
            return response_data
        else:
            print("Status:", f'{status} ({i})')
            print("Execution in progress, waiting...")
            i+=1
            time.sleep(5)  # Wait for 5 seconds before polling again

def run(metadata):
    # Replace the placeholders with your actual data
    inputs = metadata.inputs
    CLIENT_ID = inputs.get("stk_client_id")
    CLIENT_KEY = inputs.get("stk_client_key")
    ACCOUNT_SLUG = 'stackspot'
    QC_SLUG = 'container-image-checker'
    current_directory = os.getcwd()  # Get the current working directory

    # Step 1: Detect Dockerfiles in the repository
    dockerfiles = []
    for root, dirs, files in os.walk(current_directory):
        for file in files:
            if file == "Dockerfile":  # Detect Dockerfile
                dockerfiles.append(os.path.join(root, file))

    if not dockerfiles:
        print("\n\033[36mNo Dockerfiles found in the repository.\033[0m")
        return

    print(f"\n\033[36m{len(dockerfiles)} Dockerfile(s) detected in the repository.\033[0m")

    all_vulnerabilities = []
    # Step 2: Process each Dockerfile
    for dockerfile_path in dockerfiles:
        print(f'\n\033[36mProcessing Dockerfile: {dockerfile_path}\033[0m')

        # Open the Dockerfile and read its content
        with open(dockerfile_path, 'r') as file:
            dockerfile_content = file.read()

        try:
            # Execute the steps to get the updated Dockerfile content
            access_token = get_access_token(ACCOUNT_SLUG, CLIENT_ID, CLIENT_KEY)
            execution_id = create_rqc_execution(QC_SLUG, access_token, dockerfile_content)
            execution_status = get_execution_status(execution_id, access_token)

           # Extract the result
            result = execution_status['result']
            json_part = extract_json_from_result(result)  # Extract the JSON part
            result_data = json.loads(json_part)  # Parse the JSON

            #print(f"\n\033[36mRESULT DATA:\033[0m {result_data}")

            dockerfile_content = result_data.get('dockerfile')  # This is the Dockerfile content as a string
            #print(f"\n\033[36mDOCKERFILE RESULT:\033[0m {dockerfile_result}")
            vulnerabilities = result_data.get('vulnerabilities', [])  # This is the list of vulnerabilities

            if not vulnerabilities:
                # If there are no vulnerabilities, print a message indicating no update is needed
                print(f"\n\033[36mNo update needed for Dockerfile: {dockerfile_path}\033[0m")
            else:
                # Step 4: List vulnerabilities found
                print(f"\n\033[36mTotal vulnerabilities detected: {len(vulnerabilities)}\033[0m")
                for vulnerability in vulnerabilities:
                    print(f"- {vulnerability}")
                    all_vulnerabilities.append(f"{dockerfile_path}: {vulnerability}")

                if dockerfile_content:
                    # Step 5: Update the Dockerfile with the new content
                    print(f"\n\033[36mUpdating Dockerfile: {dockerfile_path}\033[0m")
                    with open(dockerfile_path, 'w') as file:
                        file.write(dockerfile_content)
                else:
                    # If the result is None, print a message indicating no vulnerabilities
                    print(f"\n\033[36mNo update needed for Dockerfile: {dockerfile_path}\033[0m")

        except KeyError as e:
            print(f"KeyError: {e} - Check if the key 'steps', 'step_result' or 'answer' is present in the response.")
        except IndexError as e:
            print(f"IndexError: {e} - Check if the list 'steps' contains enough elements.")
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e} - Check if the JSON string is formatted correctly.")
        except Exception as e:
            print(f"Unexpected error: {e}")

    save_output("vulnerabilities", all_vulnerabilities)