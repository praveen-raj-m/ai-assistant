
import os
import json
from datetime import datetime
import fitz  # PyMuPDF

MAX_TOKENS_PER_CHUNK = 300  # tune this based on your LLM context size


def estimate_tokens(text: str) -> int:
    return int(len(text.split()) * 1.3)


def extract_breadcrumbs_from_text(text: str) -> list:
    # Dummy heuristic for demo — later replace with real heading detection
    lines = text.strip().split("\n")
    for line in lines:
        if len(line.strip()) > 5 and not line.strip().startswith("•") and line[0].isupper():
            return ["Section", line.strip()]
    return ["Untitled"]


def chunk_text_by_paragraphs(text: str, max_tokens: int) -> list:
    paragraphs = text.split("\n\n")
    current_chunk = ""
    chunks = []

    for para in paragraphs:
        if not para.strip():
            continue

        temp = current_chunk + "\n\n" + para
        if estimate_tokens(temp) > max_tokens:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk = temp

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def chunk_document(file_path):
    doc_name = os.path.splitext(os.path.basename(file_path))[0]
    chunks = []
    chunk_index = 0

    doc = fitz.open(file_path)
    total_pages = len(doc)

    for page_number in range(total_pages):
        page = doc.load_page(page_number)
        raw_text = page.get_text()

        if not raw_text.strip():
            continue

        logical_chunks = chunk_text_by_paragraphs(raw_text, MAX_TOKENS_PER_CHUNK)

        for i, chunk_text in enumerate(logical_chunks):
            breadcrumbs = extract_breadcrumbs_from_text(chunk_text)
            token_count = estimate_tokens(chunk_text)

            chunks.append({
                "chunk_id": f"{doc_name}_{page_number+1:03}_{i+1:02}",
                "source": os.path.basename(file_path),
                "page_number": page_number + 1,
                "breadcrumbs": breadcrumbs,
                "text": chunk_text,
                "ref_ids": [],
                "chunk_index": chunk_index,
                "token_count": token_count,
                "created_at": datetime.utcnow().isoformat()
            })

            chunk_index += 1

    # Save chunks to JSON
    out_path = f"data/chunks/{doc_name}.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump({
            "document_name": f"{doc_name}.pdf",
            "chunked_at": datetime.utcnow().isoformat(),
            "total_pages": total_pages,
            "total_chunks": len(chunks),
            "chunks": chunks
        }, f, indent=2)

    return chunks