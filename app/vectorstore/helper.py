from typing import List, Dict
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import spacy
nlp = spacy.load("en_core_web_sm")

# ✅ Load embedding model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def chunk_transcript(video_name: str, transcript: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
    doc = nlp(transcript)
    sentences = [sent.text.strip() for sent in doc.sents]
    chunks = []
    current_chunk = []
    current_len = 0
    i = 0

    while i < len(sentences):
        sentence = sentences[i]
        sentence_len = len(sentence.split())

        if current_len + sentence_len <= chunk_size:
            current_chunk.append(sentence)
            current_len += sentence_len
            i += 1
        else:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "video_name": video_name,
                "chunk_id": len(chunks),
                "chunk": chunk_text
            })
            # Slide back for overlap
            overlap_tokens = 0
            current_chunk = []
            while overlap_tokens < overlap and i > 0:
                i -= 1
                overlap_tokens += len(sentences[i].split())
            current_len = 0

    # Add the last chunk
    if current_chunk:
        chunks.append({
            "video_name": video_name,
            "chunk_id": len(chunks),
            "chunk": " ".join(current_chunk)
        })

    return chunks

# Example: List of dicts like [{"video_name": "Vid1", "chunk_id": 0, "chunk": "Text..."}]
def embed_and_store_in_faiss(chunks):
    # Extract chunk texts
    chunk_texts = [chunk["chunk"] for chunk in chunks]
    
    # Compute embeddings
    embeddings = model.encode(chunk_texts, show_progress_bar=True, convert_to_numpy=True)
    
    # Create FAISS index (assumes L2 distance, can also use cosine similarity)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)  # or use IndexFlatIP for cosine similarity
    index.add(embeddings)

    # Store metadata separately
    metadata = []
    for chunk in chunks:
        metadata.append({
            "video_name": chunk["video_name"],
            "chunk_id": chunk["chunk_id"],
            "chunk": chunk["chunk"]
        })

    return index, metadata

def search_faiss(index, metadata, query, top_k=3):
    # Embed the query
    query_embedding = model.encode([query], convert_to_numpy=True)
    
    # Search in the index
    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for idx, i in enumerate(indices[0]):
        result = metadata[i].copy()  # Copy to avoid modifying original
        result["distance"] = float(distances[0][idx])  # Convert numpy float to native float
        results.append(result)
    
    return results

