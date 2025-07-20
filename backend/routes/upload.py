from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from utils.chunker import chunk_document
from utils.ollama_embed import get_embedding
from utils.qdrant_client import upsert_chunks
from utils.json_storage import save_chunks



upload_bp = Blueprint('upload', __name__)
UPLOAD_FOLDER = 'data/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @upload_bp.route('/upload', methods=['POST'])
# def upload():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     filename = secure_filename(file.filename)
#     file_path = os.path.join(UPLOAD_FOLDER, filename)
#     file.save(file_path)

#     chunks = chunk_document(file_path)
#     for chunk in chunks:
#         chunk["vector"] = get_embedding(chunk["text"])


#     upsert_chunks(chunks)
#     return jsonify({
#     "status": "success",
#     "filename": filename,
#     "chunk_count": len(chunks),
#     "message": f"{len(chunks)} chunks created and embedded to Qdrant for '{filename}'",
#     "chunks": chunks  # preview
# })

@upload_bp.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    return jsonify({'message': 'File uploaded...', 'file_path': file_path, 'filename': filename})


@upload_bp.route('/chunk', methods=['POST'])
def chunk():
    data = request.json
    file_path = data['file_path']
    filename = data['filename']

    chunks = chunk_document(file_path)
    save_chunks(filename, chunks)  # optional
    return jsonify({'message': f'Chunked: {len(chunks)} chunks.. Embedding in progress using nomic-embed-text', 'chunks': chunks})


@upload_bp.route('/embed', methods=['POST'])
def embed():
    chunks = request.json['chunks']
    for chunk in chunks:
        chunk['vector'] = get_embedding(chunk['text'])
    return jsonify({'message': 'Ollama Embedding complete..', 'chunks': chunks})


@upload_bp.route('/upsert', methods=['POST'])
def upsert():
    chunks = request.json['chunks']
    upsert_chunks(chunks)
    return jsonify({'message': 'VDB updated'})

