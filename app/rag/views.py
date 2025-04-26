from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .rag_pipeline import RAGPipeline, create_dummy_vectorstore
from .helper import HuggingFaceLLM

def get_rag_pipeline(query):
    if not hasattr(get_rag_pipeline, "pipeline"):
        print("⏳ Initializing real RAG pipeline...")

        # Fetch real transcripts dynamically (replace with your own endpoint if needed)
        response = requests.get("https:///api/youtubetranscript/fetch-transcript/",params={"query": query},
    auth=("", ""))
        if response.status_code != 200:
            raise ValueError("Unable to fetch transcripts.")

        transcript_data = response.json().get("results", [])

        vectorstore = create_vectorstore(transcript_data)

        llm = HuggingFaceLLM(model_id="google/gemma-2b")
        prompt_template = """You are a helpful assistant.
Use context below to answer questions:

{context}

Question: {query}
Answer:"""

        get_rag_pipeline.pipeline = RAGPipeline(
            vectorstore=vectorstore,
            embedding_model=None,  # Embedding handled inside FAISS setup
            llm_model=llm,
            prompt_template_str=prompt_template
        )
        print("Real RAG pipeline ready.")
    return get_rag_pipeline.pipeline

@csrf_exempt
def rag_query(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            query = body.get("query", "")
            if not query:
                return JsonResponse({"error": "No query provided"}, status=400)

            rag_pipeline = get_rag_pipeline(query)  # 👈 Pass query here
            response = rag_pipeline.generate_rag_response(query)
            return JsonResponse({"response": response}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "POST request required"}, status=405)