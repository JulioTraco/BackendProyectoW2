import requests

# 1. Login para obtener el token
response = requests.post("http://localhost:8000/login", data={
    "username": "julio123",
    "password": "123456"
})
TOKEN = response.json()["access_token"]

# 2. /users/me con el token en el header
headers = {
    "Authorization": f"Bearer {TOKEN}"
}
response = requests.get(
    "http://localhost:8000/users/me",
    headers=headers
)
print(response.status_code)
print(response.json())