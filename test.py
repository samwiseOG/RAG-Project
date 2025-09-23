import requests

response = requests.get("http://api.baiyi-sam.site/ollama")

print(response.text)