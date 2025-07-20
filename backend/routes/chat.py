from flask import Blueprint, request, jsonify
from utils.ollama_embed import get_embedding
from utils.qdrant_client import client, QDRANT_COLLECTION
import requests

chat_bp = Blueprint("chat", __name__)

OLLAMA_CHAT_URL = "http://localhost:11434/api/generate"
CHAT_MODEL = "llama3"  # or any model you have pulled
@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get("query", "")
    send_to_llm = data.get("send", True)

    if not user_query:
        return jsonify({"error": "Query missing"}), 400

    query_vec = get_embedding(user_query)

    search_results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vec,
        limit=5,
        with_payload=True
    )

    context = "\n\n".join([hit.payload["text"] for hit in search_results])
    prompt = f"""Use the following context to answer the question:

{context}

Question: {user_query}
Answer:"""

    if not send_to_llm:
        return jsonify({"prompt": prompt})

    response = requests.post(OLLAMA_CHAT_URL, json={
        "model": CHAT_MODEL,
        "prompt": prompt,
        "stream": False
    })

    if not response.ok:
        return jsonify({"error": "Failed to get response from Ollama"}), 500

    output = response.json().get("response", "")
    return jsonify({
        "prompt": prompt,
        "response": output
    })
