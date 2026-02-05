from flask import Flask, request
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from vdb.access import add_to_qdrant

from server.agent import query_rag
from vdb.util import load_documents, split_documents

from werkzeug.utils import secure_filename
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'data')
DEFAULT_COLLECTION_NAME = os.getenv('DEFAULT_COLLECTION_NAME', 'my_collection')

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
    # try:
    # Get collection name from request or use default
    coll_name = request.form.get('collection_name', DEFAULT_COLLECTION_NAME)
    
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_qdrant(chunks, coll_name=coll_name)
    # except Exception as e:
    #     return e, 500
    return 'file uploaded', 201



@app.route("/ollama", methods=['GET'])
def get_response():
    query = request.args.get('query')
    # enhanced_query = enhance_query(query)
    #print(enhanced_query)
    if query == "test":
        return "test successful", 200
    response = query_rag(query_text=query)
    return response, 200




if __name__ == "__main__":
    app.run(host = "0.0.0.0", port=5001, debug=True)