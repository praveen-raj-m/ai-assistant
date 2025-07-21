# AI Navigation Assistant – Full RAG Pipeline

This project is a full-stack AI assistant that helps users navigate complex documents (like tool manuals or contracts) using Retrieval-Augmented Generation (RAG). It is built with Angular (frontend), Flask (backend), and Ollama (for local embedding and LLM inference), and Qdrant (vector DB).

---

## End-to-End Pipeline

### Document Upload

* **Frontend**: User uploads `.pdf` or `.docx` files.
* **Backend**: Flask receives file, saves it, and begins processing.

---

###  Chunking Logic

#### Goals

| Feature             | Strategy                                                               |
| ------------------- | ---------------------------------------------------------------------- |
| Token safety        | Hard limit of \~300 tokens per chunk                                   |
| Contextuality       | Sliding window overlap between chunks                                  |
| Hierarchy detection | Dummy breadcrumb extraction from capitalized non-bullet lines          |
| Page metadata       | Each chunk tagged with page number                                     |
| Cross-linking       | `prev_chunk`, `next_chunk`, and optionally `ref_ids` like “see page 5” |
| Local backup        | Saved as `.json` in `/data/chunks`                                     |

#### Chunk JSON Format

```json
{
  "chunk_id": "ToolManual_075_01",
  "page_number": 75,
  "breadcrumbs": ["Authorization", "Step 1 – Record Review"],
  "text": "...",
  "ref_ids": ["ToolManual_085_02"],
  "chunk_index": 120,
  "token_count": 115,
  "created_at": "2025-07-19T15:03:00Z"
}
```

---

###  Embedding & Storing

* Uses **`nomic-embed-text`** model via Ollama
* Each chunk is converted to a **768-d vector**
* Stored in **Qdrant** with full payload (chunk text, source, page, etc.)
* Local `.json` file is also saved for recovery/debug

---

### Chat Flow

* **User Query** → embedded
* Top-5 matching chunks retrieved from Qdrant
* Duplicates filtered out
* Prompt built with:

  * Sectioned + paginated chunk text
  * Clear AI instructions
* Final prompt shown in UI before calling LLM
* Response streamed back to UI

---

## Prompting Strategy

```text
You are an AI assistant helping a user navigate a technical manual.
Use the context to answer accurately. If not found, say so.

--- MANUAL CONTEXT START ---
[Page 75] Authorization > Step 1 – Record Review
1. Verify name...
...
--- MANUAL CONTEXT END ---

User: How do I validate the provider?
AI:
```

---

## Tech Stack

| Layer     | Tech                                  |
| --------- | ------------------------------------- |
| Frontend  | Angular 17 + Vite + HTML/CSS          |
| Backend   | Flask (Python)                        |
| LLM       | Ollama (local) with `llama3`, `nomic` |
| Vector DB | Qdrant (local, HTTP API)              |
| Parsing   | PyMuPDF for PDF extraction            |
| Storage   | Local `.json` for debug + backups     |

---

## Setup Instructions

### Install Ollama Models

```bash
ollama pull nomic-embed-text
ollama pull llama3
```

### Backend (Flask)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python runserver.py
```

### Qdrant (Local)

```bash
docker run -p 6333:6333 -v $(pwd)/qdrant_data:/qdrant/storage qdrant/qdrant
```

### 🖥️ Frontend (Angular)

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:4200`

---

## C# Reimplementation Idea

You can replicate this pipeline in .NET using:

* `IFormFile` for file upload
* `PdfPig` or `PdfSharp` for parsing
* `HttpClient` for embedding/LLM API calls
* `System.Text.Json` for chunk storage
* `HttpClient` → Qdrant HTTP API

---

## Known Limitations

| Area       | Risk / Limitation                      |
| ---------- | -------------------------------------- |
| Chunking   | Heuristic-based heading detection      |
| Embedding  | Only 768-dim from `nomic-embed-text`   |
| Retrieval  | Cosine similarity only (no hybrid yet) |
| Prompting  | No token truncation or reranking       |
| References | No actual `ref_id` postprocessing yet  |

---

## Future Enhancements

* [ ] Token budget pruning
* [ ] Section-aware merging
* [ ] Reference resolution
* [ ] Chunk scoring/reranking
* [ ] UI search, filters, highlights
* [ ] Streaming LLM chat

---

## 📂 File Layout

```
ai-assistant/
│
├── backend/
│   ├── routes/        ← Flask routes: upload, chat
│   ├── utils/         ← Chunking, embedding, Qdrant
│   └── runserver.py
│
├── frontend/
│   ├── src/app/pages  ← Angular screens: home, chat
│   └── styles/        ← Minimal CSS
│
├── data/chunks/       ← Local chunk JSON backups
└── qdrant_data/        ← Mounted Qdrant volume
```

---


