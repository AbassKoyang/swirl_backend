import requests


endpoint = "http://localhost:8000/api/categories/"

name = input("Name: ")
slug = input("Slug: ")
data = {
    'name': name,
    'slug': slug,
}
response = requests.post(endpoint, json=data);