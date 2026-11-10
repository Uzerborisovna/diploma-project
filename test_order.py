import requests

TOKEN = "b174d444c15778a2b5f5ff4a7aef60be2891961a"
URL = "http://127.0.0.1:8000/api/orders/create/"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

data = {
    "contact_id": 1,
    "items": [
        {"product_id": 1, "quantity": 2}
    ]
}

response = requests.post(URL, headers=headers, json=data)
print(response.status_code)
print(response.json())
