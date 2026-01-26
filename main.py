import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, AsyncGenerator

from fastapi import FastAPI, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from rag.config import settings
from rag.ingest import build_chunks_for_file, supportedFileTypes as SUPPORTED_EXT
from rag.retreive import add_documents, similarity_search, build_citations, get_collection
from rag.llm import stream_llm_answer
from rag.utils import clean_text



app = FastAPI(title="Portfolio RAG API", version="1.0.0")

# ✅ IMPORTANT: Update this to match your UI domain(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite
        "http://localhost:3000",  # Next.js

        "https://shubhamsarpal.com/",
        "https://www.shubhamsarpal.com",

        "https://my-app-production-0a84.up.railway.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    _ = get_collection()
    return {"ok": True, "collection": settings.collection_name}


@app.post("/ingest")
async def ingest(files: List[UploadFile] = File(...)):
    indexed_files = 0
    total_chunks = 0

    for f in files:
        ext = Path(f.filename).suffix.lower()

        # ✅ Only allow supported files (PDF)
        if ext not in SUPPORTED_EXT:
            continue

        file_id = str(uuid.uuid4())[:8]
        dest = UPLOAD_DIR / f"{file_id}_{Path(f.filename).name}"
        dest.write_bytes(await f.read())

        chunks, metadatas = build_chunks_for_file(dest)

        if not chunks:
            continue

        ids = [f"{dest.name}::chunk::{i}" for i in range(len(chunks))]
        total_chunks += add_documents(chunks, metadatas, ids)
        indexed_files += 1

    return {
        "indexed_files": indexed_files,
        "chunks_added": total_chunks,
        "collection_name": settings.collection_name,
    }


def build_context_block(docs: List[str], metas: List[Dict[str, Any]]) -> str:
    parts = []
    total = 0

    for d, m in zip(docs, metas):
        label = f"[Source: {m.get('source','unknown')} | chunk_index: {m.get('chunk_index','?')}]"
        block = f"{label}\n{clean_text(d)}\n"

        if total + len(block) > settings.max_context_chars:
            break

        parts.append(block)
        total += len(block)

    return "\n---\n".join(parts)


def sse(event: str, data: Any) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/chat/stream")
async def chat_stream(message: str = Form(...), mode: str = Form("recruiter")):
    docs, metas, ids, distances = similarity_search(message, settings.top_k)
    citations = build_citations(docs, metas, ids)
    context = build_context_block(docs, metas)

    followups = [
        "Summarize my experience for a Staff Engineer role in 5 bullets.",
        "List my strongest tech stack + what I owned end-to-end.",
        "Share a STAR story from my most impactful project.",
    ]

    async def gen() -> AsyncGenerator[str, None]:
        yield sse("citations", {"citations": citations})
        yield sse("followups", {"followups": followups})

        try:
            async for token in stream_llm_answer(mode=mode, message=message, context=context):
                yield sse("token", {"token": token})
        except Exception as e:
            yield sse("error", {"message": str(e)})
            return

        yield sse("done", {"ok": True})

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/chat")
async def chat_get(
    message: str = Query(...),
    mode: str = Query("recruiter"),
):
    docs, metas, ids, _ = similarity_search(message, settings.top_k)
    citations = build_citations(docs, metas, ids)
    context = build_context_block(docs, metas)

    # ✅ collect full answer from streaming generator (no SSE)
    answer_parts = []
    async for token in stream_llm_answer(mode=mode, message=message, context=context):
        answer_parts.append(token)

    answer = "".join(answer_parts)

    return {
        "answer": answer,
        "citations": citations,
        "mode": mode,
        "top_k": settings.top_k,
    }



