import requests

url = "http://127.0.0.1:8000/api/v1/users/me"
headers = {
    "Authorization": "Bearer dev_mock_token_123"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
