from flask import Flask, request
import ollama
import requests 
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm.prompts import enhance_query
from server.agent import query_rag
from file_util import get_text_from_pdf
from vdb.util import text_2_vec

from werkzeug.utils import secure_filename
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = "/home/sam/Documents/Projects/RAG/RAG-Project/app/tmp"

@app.route("/embed", methods=['POST'])
def load_file():
    if 'document' not in request.files:
        return 'No file in the request',400
    file = request.files['document']
    if file:
        filename = secure_filename(file.filename)
        path_to_file =  os.path.join(app.config['UPLOAD_FOLDER'],filename)
        file.save(path_to_file)
    else: 
        return 'No file in the request',400
    try:
        text = get_text_from_pdf(path_to_file)
    except Exception as e:
        return 'error during text extraction' + {str(e)}, 500
    try:
        text_2_vec(text, path=path_to_file, coll_name="RAG-Project")
    except Exception as e:
        return 'error during vectorization' + {str(e)}, 500
    return 'file uploaded', 201



@app.route("/ollama", methods=['GET'])
def get_response():
    query = request.args.get('query')
    # enhanced_query = enhance_query(query)
    #print(enhanced_query)
    response = query_rag(query_text=query)
    return response, 200




if __name__ == "__main__":
    app.run(host = "0.0.0.0", port=5001)