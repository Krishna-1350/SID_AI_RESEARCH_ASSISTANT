from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
import requests

from sentence_transformers import SentenceTransformer
from app.vectorstore.helper import chunk_transcript, embed_and_store_in_faiss, search_faiss

# ✅ Load embedding model once
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Global variables for reuse (optional)
index = None
metadata = []

class TranscriptRAGView(APIView):
    """
    Orchestrates: 
    1. Fetch transcript using YouTube API
    2. Chunk and embed using SentenceTransformer + FAISS
    3. Search similar chunks for a query
    """

    def post(self, request):
        query = request.data.get("query")
        chunk_size = request.data.get("chunk_size", 500)
        overlap = request.data.get("overlap", 100)
        top_k = request.data.get("top_k", 3)

        if not query:
            return Response({"error": "Query is required."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Step 1: Call internal fetch-transcript API (GET with query param)
        response = requests.get("http://localhost:8000/api/youtubetranscript/fetch-transcript/", params={"query": query})
        if response.status_code == 200:
                data = response.json()
                # return Response({'msg':data['results'][0].keys()}, status=status.HTTP_200_OK)
                print({'msg':data['results'][0].keys()})  

        if response.status_code != 200:
            return Response({"error": "Failed to fetch transcripts", "details": response.json()}, status=response.status_code)

        transcript_data = response.json().get("results", [])
        
        all_chunks = []

        # ✅ Step 2: Chunk all transcripts
        for item in transcript_data:
            video_name = item["video_name"]
            transcript = item["transcript"]
            chunks = chunk_transcript(video_name, transcript, chunk_size=chunk_size, overlap=overlap)
            all_chunks.extend(chunks)
            

        # ✅ Step 3: Embed & Store in FAISS
        index, metadata = embed_and_store_in_faiss(all_chunks)

        # ✅ Step 4: Search
        results = search_faiss(index, metadata, query=query, top_k=top_k)

        return Response({
            "query": query,
            "matches": results
        }, status=status.HTTP_200_OK)