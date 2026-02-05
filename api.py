from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import llm

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
print(UPLOAD_FOLDER)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf"}



def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "no selected file"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "only PDF files are allowed"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    print(f"File saved to: {save_path}")
    user_id = request.form.get("user_id")
    source = request.form.get("source")

    return jsonify({
        "status": "success",
        "filename": filename,
        "saved_path": save_path,
        "user_id": user_id,
        "source": source
    }), 200

@app.route("/ollama", methods=['GET'])
def get_response():
    query = request.form.get('query')
    llm_obj = llm.llm_class()
    try:
        response = llm_obj.generate(query)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return response, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)