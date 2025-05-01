from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

from .rag_pipeline import RAGPipeline, create_dummy_vectorstore, create_vectorstore
from .helper import HuggingFaceLLM

def get_rag_pipeline(query):
    if not hasattr(get_rag_pipeline, "pipeline"):
        print("⏳ Initializing real RAG pipeline...")
        # Fetch real transcripts dynamically (replace with your own endpoint if needed)

        response = requests.post("http://localhost:8009/api/vectorstore/transcript-rag/",data={"query": query}, auth=("", ""))
        print(response.status_code)
        if response.status_code != 200:
            raise ValueError("Unable to fetch transcripts.") 

        context = response.json().get("context", '')

        # vectorstore = create_vectorstore(transcript_data)

        # llm = HuggingFaceLLM(model_id="google/gemma-2b")

        prompt_template = """You are a helpful assistant.
                            Use context below to answer questions:

                            {context}

                            Question: {query}
                            Answer:"""
        
        final_prompt = prompt_template.format(context=context, query=query)

        # Step 3: Call Ollama's LLaMA2
        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2", 
                "prompt": final_prompt,
                "stream": False
            }
        )
        print(ollama_response.status_code)
        if ollama_response.status_code != 200:
            raise ValueError("Ollama LLM request failed.")

        answer = ollama_response.json().get("response", "").strip()

        # Step 4: Store it in a callable format for reuse
        def run_rag_pipeline(_query):
            return answer  # You can modify this to regenerate if needed

        get_rag_pipeline.pipeline = run_rag_pipeline
        print("RAG pipeline with Ollama ready.")
    
    return get_rag_pipeline.pipeline

@csrf_exempt
def rag_query(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            query = body.get("query", "")
            if not query:
                return JsonResponse({"error": "No query provided"}, status=400)

            rag_pipeline = get_rag_pipeline(query) 
            response = rag_pipeline(query)          
            return JsonResponse({"response": response}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "POST request required"}, status=405)