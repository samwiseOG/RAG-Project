from flask import Flask
import ollama
import requests 
from setup import *
app = Flask(__name__)

@app.route("/embed", methods=['POST'])

def load_file():
    if 'document' not in requests.files:
        return 'No file in the request',400
    file = requests.files['document']
    try:
        text = get_text_from_pdf(file)
    except Exception as e:
        return 'error during text extraction' + {str(e)}, 500
    try:
        text_2_vec(text)
    except Exception as e:
        return 'error during vectorization' + {str(e)}, 500
    return 'file uploaded', 201


def get_response():
    return str(ollama.embeddings(model='nomic-embed-text', prompt='The sky is blue because of rayleigh scattering'))

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port=5000)