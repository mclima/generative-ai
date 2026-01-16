import requests

def get_json(url: str, params: dict = None, headers: dict = None):
    response = requests.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()
