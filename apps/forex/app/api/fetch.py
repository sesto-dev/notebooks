import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def _make_request(method, endpoint, params=None, data=None):
    base_url = os.environ.get('MT5_API_URL')
    url = f"{base_url}{endpoint}"
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise