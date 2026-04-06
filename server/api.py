from flask import Flask, request
import sys
import os
from pathlib import Path


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from vdb.access import add_to_qdrant, get_collections, create_collection_with_name

from server.agent import query_rag
from vdb.util import load_documents, split_documents

from werkzeug.utils import secure_filename
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'data')

@app.route("/collections", methods=['GET'])
def get_available_collections():
    try:
        collections = get_collections()
        return {"collections": collections}, 200
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/collections", methods=['POST'])
def create_collection():
    try:
        data = request.get_json()
        collection_name = data.get('name')
        
        if not collection_name:
            return {"error": "Collection name is required"}, 400
        
        # Sanitize collection name (alphanumeric, hyphens, underscores)
        if not all(c.isalnum() or c in '-_' for c in collection_name):
            return {"error": "Collection name can only contain alphanumeric characters, hyphens, and underscores"}, 400
        
        success = create_collection_with_name(collection_name, "COSINE")
        if success:
            return {"message": "Collection created successfully", "collection": collection_name}, 201
        else:
            return {"error": "Collection already exists"}, 409
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/embed", methods=['POST'])
def load_file():
    if 'document' not in request.files:
        return 'No file in the request',400
    file = request.files['document']
    collection_name = request.form.get('collection', 'my_collection')
    if file:
        filename = secure_filename(file.filename)
        path_to_file =  os.path.join(app.config['UPLOAD_FOLDER'],filename)
        file.save(path_to_file)
    else: 
        return 'No file in the request',400
    try:
        # text = get_text_from_pdf(path_to_file)
        documents = load_documents()
        chunks = split_documents(documents)
        add_to_qdrant(chunks, coll_name=collection_name)
    except Exception as e:
        return 'error during text extraction' + {str(e)}, 500
    return 'file uploaded', 201



@app.route("/ollama", methods=['GET'])
def get_response():
    query = request.args.get('query')
    collection_name = request.args.get('collection', 'RAG-Project')
    # enhanced_query = enhance_query(query)
    #print(enhanced_query)
    response = query_rag(query_text=query, coll_name=collection_name)
    return response, 200




if __name__ == "__main__":
    app.run(host = "0.0.0.0", port=5001)