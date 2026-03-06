from vercel_runtime import VercelRequest, VercelResponse
from rag_chat import retrieve_documents, generate_answer

# -----------------------------
# Precomputed embeddings dictionary
# -----------------------------
# Example: mapping questions to their embeddings
# You can load this from a JSON or pickle file in root
import json
import os

EMBEDDINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "precomputed_embeddings.json")
precomputed_embeddings = {}

if os.path.exists(EMBEDDINGS_FILE):
    with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
        precomputed_embeddings = json.load(f)

# -----------------------------
# Vercel API handler
# -----------------------------
def handler(req: VercelRequest):
    try:
        body = req.json
        question = body.get("question", "").strip()
        if not question:
            return VercelResponse.json({"error": "Question is required"}, status=400)

        # Use precomputed embedding if exists, else return error
        query_embedding = precomputed_embeddings.get(question)
        if not query_embedding:
            return VercelResponse.json({"error": "Embedding not found for this question"}, status=400)

        # Retrieve relevant chunks from Pinecone
        docs = retrieve_documents(query_embedding, top_k=5)

        if not docs:
            return VercelResponse.json({"answer": "No relevant documents found."})

        # Generate final answer using Groq
        answer = generate_answer(question, docs)

        return VercelResponse.json({"answer": answer})

    except Exception as e:
        # Return clean JSON error for frontend
        return VercelResponse.json({"error": str(e)}, status=500)
