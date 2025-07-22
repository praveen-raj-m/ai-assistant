import os
import uuid
from langchain.document_loaders import PyPDFLoader
from langchain.schema.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List


def load_pdf_chunks(pdf_path: str, chunk_size=300, chunk_overlap=50) -> List[Document]:
    """
    Loads a PDF using PyPDFLoader and chunks the text while preserving metadata.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()  # Returns list of Document with metadata["page"]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )

    all_chunks = []
    for page in pages:
        chunks = splitter.split_text(page.page_content)
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk.strip(),
                metadata={
                    "source": os.path.basename(pdf_path),
                    "page_number": page.metadata.get("page", None),
                    "chunk_index": i,
                    "chunk_id": str(uuid.uuid4())
                }
            )
            all_chunks.append(doc)

    return all_chunks


def print_chunks(chunks: List[Document]):
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i + 1} ---")
        print("Metadata:", chunk.metadata)
        print("Content:\n", chunk.page_content)
        print("-" * 50)


if __name__ == "__main__":
    # ==== Replace with your PDF path ====
    pdf_file_path = "example.pdf"  # Example: 'reports/financials_q1.pdf'

    try:
        chunked_documents = load_pdf_chunks(pdf_file_path)
        print_chunks(chunked_documents)
    except Exception as e:
        print(f"Error: {e}")
