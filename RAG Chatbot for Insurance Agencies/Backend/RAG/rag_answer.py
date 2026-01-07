import os
import numpy as np
from openai import OpenAI
import faiss

CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-5.2")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

client = OpenAI()

def embed_query(query: str) -> np.ndarray:
    resp = client.embeddings.create(model=EMBED_MODEL, input=[query])
    vec = np.array([resp.data[0].embedding], dtype="float32")
    faiss.normalize_L2(vec)
    return vec

def retrieve(query: str, index, chunks: list[str], k: int = 4) -> list[str]:
    qvec = embed_query(query)
    scores, ids = index.search(qvec, k)
    results = []
    for i in ids[0]:
        if i == -1:
            continue
        results.append(chunks[i])
    return results

def generate_answer(user_question: str, retrieved_chunks: list[str]) -> str:
    context = "\n\n".join(retrieved_chunks)

    response = client.responses.create(
        model=CHAT_MODEL,
        instructions=(
            "You are an Insurance Agency Customer Care assistant. "
            "Use only the provided context to answer. "
            "If the answer is not in the context, say you do not have it in the documents "
            "and offer to connect to a human agent. "
            "Keep it short, friendly, and clear."
        ),
        input=[
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{user_question}"}
        ],
    )
    return response.output_text