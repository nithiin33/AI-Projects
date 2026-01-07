import os
from fastapi import FastAPI
from pydantic import BaseModel

from rag.pdf_to_text import pdf_to_text
from rag.chunking import chunk_text
from rag.embed_store import build_and_save_index, load_index
from rag.rag_answer import retrieve, generate_answer

app = FastAPI()

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PDF_PATH = os.path.join(DATA_DIR, "knowledge.pdf")
INDEX_PATH = os.path.join(DATA_DIR, "index.faiss")
META_PATH = os.path.join(DATA_DIR, "chunks.json")

index = None
chunks = None

class ChatIn(BaseModel):
    message: str

@app.post("/ingest")
def ingest():
    global index, chunks
    text = pdf_to_text(PDF_PATH)
    chunks = chunk_text(text, chunk_tokens=450, overlap_tokens=80)
    build_and_save_index(chunks, INDEX_PATH, META_PATH)
    index, chunks = load_index(INDEX_PATH, META_PATH)
    return {"status": "ok", "chunks": len(chunks)}

@app.post("/chat")
def chat(payload: ChatIn):
    global index, chunks
    if index is None or chunks is None:
        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            index, chunks = load_index(INDEX_PATH, META_PATH)
        else:
            return {"answer": "Knowledge base not ingested yet. Call ingest first."}

    hits = retrieve(payload.message, index, chunks, k=4)
    answer = generate_answer(payload.message, hits)
    return {"answer": answer, "sources": hits}