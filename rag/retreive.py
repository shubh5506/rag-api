from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from .config import settings
from .utils import safe_snipet

_client = None
_collection = None
_embedder = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(settings.embedding_model)
    return _embedder


def get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection

    _client = chromadb.PersistentClient(
        path=settings.chroma_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )

    _collection = _client.get_or_create_collection(name=settings.collection_name)
    return _collection


def add_documents(texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> int:
    col = get_collection()
    col.add(documents=texts, metadatas=metadatas, ids=ids)
    return len(texts)


def similarity_search(query: str, top_k: int):
    embedder = get_embedder()
    col = get_collection()

    q_emb = embedder.encode([query], normalize_embeddings=True).tolist()[0]

    res = col.query(
        query_embeddings=[q_emb],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    ids = res.get("ids", [[]])[0]          # ids still available
    distances = res.get("distances", [[]])[0]

    return docs, metas, ids, distances


def build_citations(docs: List[str], metas: List[Dict[str, Any]], ids: List[str]) -> List[Dict[str, Any]]:
    out = []
    for d, m, i in zip(docs, metas, ids):
        out.append({
            "source": m.get("source", "unknown"),
            "chunk_id": i,
            "snippet": safe_snipet(d, 200),
            "metadata": m,
        })
    return out


if __name__ == "__main__":
    print("Starting Chroma test...")
    

    col = get_collection()
    print("Collection loaded:", col.name)


    add_documents(
        ["My name is Shubham and I build RAG chatbots using FastAPI + React."],
        [{"source": "manual_test"}],
        ["test1"]
    )


    docs, metas, ids, distances = similarity_search("What do you build?", top_k=1)

   
   

# print("\n Top result:", docs[0])
# print("ID:", ids[0])
# print("Distance:", distances[0])
# print("Metadata:", metas[0])

