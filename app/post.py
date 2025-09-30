import requests

file_path = input()

with open(file_path, 'rb') as f:
    files = {'document': f}
    response = requests.post("http://api.baiyi-sam.site/embed")
print(response.text)