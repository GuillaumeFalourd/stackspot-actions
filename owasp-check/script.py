import subprocess
import requests
import time
import json
import fnmatch

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
        print('ExecutionID:', response_data)
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
        if status in ['COMPLETED', 'FAILED']:
            return response_data
        else:
            print("Status:", f'{status} ({i})')
            print("Execution in progress, waiting...")
            i+=1
            time.sleep(5)  # Wait for 5 seconds before polling again

def calculate_risk_rate(score):
    if 0.1 <= score <= 2.0:
        return 'A - Safe'
    elif 2.1 <= score <= 4.0:
        return 'B - Low'
    elif 4.1 <= score <= 6.0:
        return 'C - Medium'
    elif 6.1 <= score <= 8.0:
        return 'D - High'
    elif 8.1 <= score <= 10.0:
        return 'E - Critical'
    else:
        return 'Unknown'

def get_all_files():
    result = subprocess.run(['git', 'ls-files'], stdout=subprocess.PIPE, text=True)
    files = result.stdout.split('\n')
    # List of patterns to exclude
    patterns = ['sast-*', '*.txt', '*.md', '*.git', 'action.*', 'rqc.*', '*.stkignore', '*.yml', '*.yaml']
    filtered_files = [file for file in files if file and not any(fnmatch.fnmatch(file, pattern) for pattern in patterns)]
    return filtered_files

def process_vulnerabilities(answer_data):
    vulnerabilities_info = []
    total_vulnerabilities = 0
    total_score = 0.0
    # Counts only if cvss-score is more than 0
    if isinstance(answer_data, list):
        for vulnerability in answer_data:
            if vulnerability['cvss-score'] > 0.0:
                total_vulnerabilities += 1
                total_score += vulnerability['cvss-score']
                vulnerabilities_info.append((vulnerability['vulnerability name'], vulnerability['cvss-score']))
                print(f"Vulnerability: {vulnerability['vulnerability name']}, Score: {vulnerability['cvss-score']}")
    elif isinstance(answer_data, dict):
        if answer_data['cvss-score'] > 0.0:
            total_vulnerabilities += 1
            total_score += answer_data['cvss-score']
            vulnerabilities_info.append((answer_data['vulnerability name'], answer_data['cvss-score']))
            print(f"Vulnerability: {answer_data['vulnerability name']}, Score: {answer_data['cvss-score']}")
    else:
        print("Unexpected data format")
    return total_vulnerabilities, total_score, vulnerabilities_info

def run(metadata):
    # Replace the placeholders with your actual data
    inputs = metadata.inputs
    CLIENT_ID = inputs.get("stk_client_id")
    CLIENT_KEY = inputs.get("stk_client_key")
    ACCOUNT_SLUG = 'stackspot'
    QC_SLUG = '???'
    CHANGED_FILES = get_all_files()
    print(f'\033[36mFiles to analyze: {CHANGED_FILES}\033[0m')

    total_score = 0.0
    total_vulnerabilities = 0
    all_vulnerabilities_info = []  # Initialize the list to store vulnerabilities info

    for file_path in CHANGED_FILES:
        print(f'\n\033[36mFile Path: {file_path}\033[0m')
        # Open the file and read its content
        with open(file_path, 'r') as file:
            file_content = file.read()

        # Move the definition of YOUR_DATA here
        YOUR_DATA = file_content

        # Execute os passos
        access_token = get_access_token(ACCOUNT_SLUG, CLIENT_ID, CLIENT_KEY)
        execution_id = create_rqc_execution(QC_SLUG, access_token, YOUR_DATA)
        execution_status = get_execution_status(execution_id, access_token)

        try:
            answer_str = execution_status['result'].strip().replace('```json', '').replace('```', '').replace('\n', '')
            answer_data = json.loads(answer_str)
            vulnerabilities, score, vulnerabilities_info = process_vulnerabilities(answer_data)
            total_vulnerabilities += vulnerabilities
            total_score += score
            all_vulnerabilities_info.extend(vulnerabilities_info)
        except KeyError as e:
            print(f"KeyError: {e} - Verifique se a chave 'steps', 'step_result' ou 'answer' está presente na resposta.")
        except IndexError as e:
            print(f"IndexError: {e} - Verifique se a lista 'steps' contém elementos suficientes.")
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e} - Verifique se a string JSON está formatada corretamente.")
        except Exception as e:
            print(f"Erro inesperado: {e}")

    if total_vulnerabilities > 0:
        average_score = total_score / total_vulnerabilities
        risk_rate = calculate_risk_rate(average_score)
        print(f"\n\033[36mAverage CVSS Score: {average_score}\033[0m")
        print(f"\033[36mRisk Rate: {risk_rate}\033[0m")
    else:
        print("No vulnerabilities found.")

    # Print summary
    print("\n\033[36mSummary of Vulnerabilities:\033[0m")
    for vulnerability_name, score in all_vulnerabilities_info:
        print(f"Vulnerability: {vulnerability_name}, Score: {score}")
    print(f"\nTotal Vulnerabilities with CVSS Score: {total_vulnerabilities}")
