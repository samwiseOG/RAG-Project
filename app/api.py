from flask import Flask
import ollama
app = Flask(__name__)

@app.route("/ollama", methods=['GET'])
def get_response():
    return str(ollama.embeddings(model='nomic-embed-text', prompt='The sky is blue because of rayleigh scattering'))

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port=5000)