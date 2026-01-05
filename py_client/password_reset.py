import requests

request_reset_endpoint = 'http://localhost:8000/api/auth/password-reset/'
request_data = {
    "email": 'abasskoyang05@gmail.com'
}
response = requests.post(request_reset_endpoint, json=request_data)
confirm_reset_endpoint = 'http://localhost:8000/api/auth/password-reset/confirm/'

print(response.json())

uid = response.json()['uid']
token = response.json()['token']
print(uid)
print(token)
new_password = input("Enter new_password")
data = {
    "token": token,
    "uid": uid,
    "new_password": new_password
}
response_2 = requests.post(confirm_reset_endpoint, json=data)
print(response_2.json())
