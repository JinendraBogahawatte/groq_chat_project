import requests

url = "http://127.0.0.1:8001/chat"
data = {"message": "Explain the importance of fast language models"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)
print(response.json())
