# backend/utils/json_storage.py
import os
import json
from datetime import datetime

CHUNK_DIR = 'data/chunks'
os.makedirs(CHUNK_DIR, exist_ok=True)

def save_chunks(document_name: str, chunks: list):
    json_path = os.path.join(CHUNK_DIR, f"{document_name}.json")
    payload = {
        "document_name": document_name,
        "chunked_at": datetime.utcnow().isoformat(),
        "total_chunks": len(chunks),
        "chunks": chunks
    }
    with open(json_path, 'w') as f:
        json.dump(payload, f, indent=2)
