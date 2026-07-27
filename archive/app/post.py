import requests

file_path = input("file to embed: ")

with open(file_path, 'r') as f:
    files = {'document': f}
    response = requests.post("http://api.baiyi-sam.site/embed",files)
print(response.text)