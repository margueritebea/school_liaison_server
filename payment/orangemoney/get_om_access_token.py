import requests
from base64 import b64encode
import os

def get_om_access_token():
    client_id = os.getenv("OM_CLIENT_ID")
    client_secret = os.getenv("OM_CLIENT_SECRET")
    consumer_key = b64encode(f"{client_id}:{client_secret}".encode()).decode()

    url = "https://api.orange.com/oauth/v3/token"
    headers = {
        "Authorization": f"Basic {consumer_key}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()

    if response.status_code == 200:
        return response_data['access_token']
    else:
        raise Exception(f"Failed to obtain access token: {response_data}")

# Example usage
# token = get_om_access_token()
# print(token)
