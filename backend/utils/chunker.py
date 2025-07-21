
import os
import json
from datetime import datetime
import fitz  # PyMuPDF

# MAX_TOKENS_PER_CHUNK = 300  # tune this based on your LLM context size


# def estimate_tokens(text: str) -> int:
#     return int(len(text.split()) * 1.3)


# def extract_breadcrumbs_from_text(text: str) -> list:
#     # Dummy heuristic for demo — later replace with real heading detection
#     lines = text.strip().split("\n")
#     for line in lines:
#         if len(line.strip()) > 5 and not line.strip().startswith("•") and line[0].isupper():
#             return ["Section", line.strip()]
#     return ["Untitled"]


# def chunk_text_by_paragraphs(text: str, max_tokens: int) -> list:
#     paragraphs = text.split("\n\n")
#     current_chunk = ""
#     chunks = []

#     for para in paragraphs:
#         if not para.strip():
#             continue

#         temp = current_chunk + "\n\n" + para
#         if estimate_tokens(temp) > max_tokens:
#             if current_chunk:
#                 chunks.append(current_chunk.strip())
#             current_chunk = para
#         else:
#             current_chunk = temp

#     if current_chunk:
#         chunks.append(current_chunk.strip())

#     return chunks


# def chunk_document(file_path):
#     doc_name = os.path.splitext(os.path.basename(file_path))[0]
#     chunks = []
#     chunk_index = 0

#     doc = fitz.open(file_path)
#     total_pages = len(doc)

#     for page_number in range(total_pages):
#         page = doc.load_page(page_number)
#         raw_text = page.get_text()

#         if not raw_text.strip():
#             continue

#         logical_chunks = chunk_text_by_paragraphs(raw_text, MAX_TOKENS_PER_CHUNK)

#         for i, chunk_text in enumerate(logical_chunks):
#             breadcrumbs = extract_breadcrumbs_from_text(chunk_text)
#             token_count = estimate_tokens(chunk_text)

#             chunks.append({
#                 "chunk_id": f"{doc_name}_{page_number+1:03}_{i+1:02}",
#                 "source": os.path.basename(file_path),
#                 "page_number": page_number + 1,
#                 "breadcrumbs": breadcrumbs,
#                 "text": chunk_text,
#                 "ref_ids": [],
#                 "chunk_index": chunk_index,
#                 "token_count": token_count,
#                 "created_at": datetime.utcnow().isoformat()
#             })

#             chunk_index += 1

#     # Save chunks to JSON
#     out_path = f"data/chunks/{doc_name}.json"
#     os.makedirs(os.path.dirname(out_path), exist_ok=True)
#     with open(out_path, 'w') as f:
#         json.dump({
#             "document_name": f"{doc_name}.pdf",
#             "chunked_at": datetime.utcnow().isoformat(),
#             "total_pages": total_pages,
#             "total_chunks": len(chunks),
#             "chunks": chunks
#         }, f, indent=2)

#     return chunks


# backend/utils/chunker_v2.py
import os
import json
from datetime import datetime
import fitz  # PyMuPDF
import re

MAX_TOKENS_PER_CHUNK = 300
TOKEN_OVERLAP = 50


def estimate_tokens(text: str) -> int:
    return int(len(text.split()) * 1.3)


def find_page_references(text: str):
    matches = re.findall(r"[Pp]age\s+(\d{1,4})", text)
    return sorted(set(map(int, matches))) if matches else []


def extract_breadcrumbs(text: str):
    lines = text.strip().split("\n")
    for line in lines:
        if len(line.strip()) > 5 and line[0].isupper():
            return ["Section", line.strip()]
    return ["Untitled"]


def sliding_chunks(paragraphs, max_tokens, overlap):
    chunks = []
    current = []
    current_token_count = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        token_count = estimate_tokens(para)

        if current_token_count + token_count > max_tokens:
            if current:
                chunks.append("\n\n".join(current))
                # overlap: retain last paragraph(s)
                overlap_chunk = []
                overlap_tokens = 0
                for p in reversed(current):
                    overlap_chunk.insert(0, p)
                    overlap_tokens += estimate_tokens(p)
                    if overlap_tokens >= overlap:
                        break
                current = overlap_chunk
                current_token_count = overlap_tokens

        current.append(para)
        current_token_count += token_count

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def chunk_document(file_path):
    doc_name = os.path.splitext(os.path.basename(file_path))[0]
    chunks = []
    chunk_index = 0

    doc = fitz.open(file_path)
    total_pages = len(doc)

    prev_chunk_id = None

    for page_number in range(total_pages):
        page = doc.load_page(page_number)
        raw_text = page.get_text()
        if not raw_text.strip():
            continue

        paragraphs = raw_text.split("\n\n")
        logical_chunks = sliding_chunks(paragraphs, MAX_TOKENS_PER_CHUNK, TOKEN_OVERLAP)

        for i, chunk_text in enumerate(logical_chunks):
            token_count = estimate_tokens(chunk_text)
            breadcrumbs = extract_breadcrumbs(chunk_text)
            page_refs = find_page_references(chunk_text)

            chunk_id = f"{doc_name}_{page_number+1:03}_{i+1:02}"

            chunk = {
                "chunk_id": chunk_id,
                "source": os.path.basename(file_path),
                "page_number": page_number + 1,
                "breadcrumbs": breadcrumbs,
                "breadcrumb_path": " > ".join(breadcrumbs),
                "text": chunk_text,
                "ref_ids": [],  # Add post-processing later
                "page_references": page_refs,
                "prev_chunk": prev_chunk_id,
                "next_chunk": None,  # Will be set in next loop
                "chunk_type": "body",
                "section_depth": len(breadcrumbs),
                "importance_score": 0.5,
                "embedding_skipped": False,
                "chunk_index": chunk_index,
                "token_count": token_count,
                "created_at": datetime.utcnow().isoformat()
            }

            if prev_chunk_id:
                chunks[-1]["next_chunk"] = chunk_id

            chunks.append(chunk)
            prev_chunk_id = chunk_id
            chunk_index += 1

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