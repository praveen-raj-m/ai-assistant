# from flask import Blueprint, request, jsonify
# from utils.ollama_embed import get_embedding
# from utils.qdrant_client import client, QDRANT_COLLECTION
# import requests

# chat_bp = Blueprint("chat", __name__)

# OLLAMA_CHAT_URL = "http://localhost:11434/api/generate"
# CHAT_MODEL = "llama3"  # or any model you have pulled
# @chat_bp.route('/chat', methods=['POST'])
# def chat():
#     data = request.json
#     user_query = data.get("query", "")
#     send_to_llm = data.get("send", True)

#     if not user_query:
#         return jsonify({"error": "Query missing"}), 400

#     query_vec = get_embedding(user_query)

#     search_results = client.search(
#         collection_name=QDRANT_COLLECTION,
#         query_vector=query_vec,
#         limit=5,
#         with_payload=True
#     )

#     context = "\n\n".join([hit.payload["text"] for hit in search_results])
#     prompt = f"""Use the following context to answer the question:

# {context}

# Question: {user_query}
# Answer:"""

#     if not send_to_llm:
#         return jsonify({"prompt": prompt})

#     response = requests.post(OLLAMA_CHAT_URL, json={
#         "model": CHAT_MODEL,
#         "prompt": prompt,
#         "stream": False
#     })

#     if not response.ok:
#         return jsonify({"error": "Failed to get response from Ollama"}), 500

#     output = response.json().get("response", "")
#     return jsonify({
#         "prompt": prompt,
#         "response": output
#     })


from flask import Blueprint, request, jsonify
from utils.ollama_embed import get_embedding
from utils.qdrant_client import client, QDRANT_COLLECTION
import requests

chat_bp = Blueprint("chat", __name__)

OLLAMA_CHAT_URL = "http://localhost:11434/api/generate"
CHAT_MODEL = "llama3"

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get("query", "")
    send_to_llm = data.get("send", True)
    temperature = data.get("temperature", 0.3)
    chat_history = data.get("history", [])

    if not user_query:
        return jsonify({"error": "Query missing"}), 400

    query_vec = get_embedding(user_query)

    search_results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vec,
        limit=10,
        with_payload=True
    )

    seen = set()
    selected_chunks = []
    for hit in search_results:
        chunk_id = hit.payload.get("chunk_id")
        text = hit.payload.get("text", "").strip()
        key = (chunk_id, text[:50])
        if key not in seen and text:
            seen.add(key)
            selected_chunks.append(hit.payload)
        if len(selected_chunks) >= 5:
            break

    context_blocks = []
    for chunk in selected_chunks:
        breadcrumb = " > ".join(chunk.get("breadcrumbs", []))
        page = chunk.get("page_number", "N/A")
        context_blocks.append(f"[Page {page}] {breadcrumb}\n{chunk['text']}")

    context = "\n\n---\n\n".join(context_blocks)

    # Include chat history if provided
    history_text = ""
    for turn in chat_history[-3:]:  # limit to last 3 turns
        history_text += f"User: {turn['user']}\nAI: {turn['ai']}\n"

    prompt = f"""
You are an AI assistant helping a user navigate a technical manual.
Use the following context to answer their latest question accurately and concisely.

--- MANUAL CONTEXT START ---
{context}
--- MANUAL CONTEXT END ---

--- CHAT HISTORY ---
{history_text}
User: {user_query}
AI:""".strip()

    if not send_to_llm:
        return jsonify({"prompt": prompt})

    response = requests.post(OLLAMA_CHAT_URL, json={
        "model": CHAT_MODEL,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    })

    if not response.ok:
        return jsonify({"error": "Failed to get response from Ollama"}), 500

    output = response.json().get("response", "")
    return jsonify({
        "prompt": prompt,
        "response": output
    })
