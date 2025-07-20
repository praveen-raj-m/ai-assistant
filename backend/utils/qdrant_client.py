from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import os
import uuid

QDRANT_COLLECTION = "navigation_doc"

client = QdrantClient("localhost", port=6333)


def ensure_collection():
    client.recreate_collection(  # ✅ force recreate with 768
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=768,  # ✅ must match nomic-embed-text
            distance=Distance.COSINE
        )
    )

def upsert_chunks(chunks_with_vectors):
    ensure_collection()
    points = [
    PointStruct(
        id=str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["chunk_id"])),  # 👈 convert to UUID
        vector=chunk["vector"],
        payload={
            "chunk_id": chunk["chunk_id"],  # include original ID as metadata
            "text": chunk["text"],
            "source": chunk["source"],
            "page_number": chunk["page_number"],
            "breadcrumbs": chunk["breadcrumbs"]
        }
    )
    for chunk in chunks_with_vectors
]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)
