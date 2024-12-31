import requests


def login_to_api():
    url = "/api/v1/auth/login"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "",
        "username": "user1@gmail.com",
        "password": "zxcv",
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        print("Login successful!")
        return response.json()
    else:
        print(f"Login failed with status code {response.status_code}")
        print(response.text)
        return None
