import requests

OLLAMA_URL = "http://localhost:11434/api/embeddings"  # assuming local

def get_embedding(text, model="nomic-embed-text"):
    response = requests.post(OLLAMA_URL, json={"model": model, "prompt": text})
    response.raise_for_status()
    return response.json()["embedding"]
