import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.embeddings.base import Embeddings
from langchain_core.documents import Document
from helper import HuggingFaceLLM

class RAGPipeline:
    def __init__(
        self,
        vectorstore,
        embedding_model: Embeddings,
        llm_model,
        prompt_template_str: str,
        top_k: int = 3,
    ):
        self.llm = llm_model
        self.prompt_template = ChatPromptTemplate.from_template(prompt_template_str)
        self.vectorstore = vectorstore
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": top_k}
        )

    def generate_rag_response(self, query: str):
        retrieved_docs = self.retriever.invoke(query)
        context_with_video_ids = ""

        for doc in retrieved_docs:
            video_id = doc.metadata.get("videoId", "N/A")
            content = doc.page_content
            context_with_video_ids += f"Context: {content}\n"
            if video_id != "N/A":
                context_with_video_ids += f"Video ID: {video_id}\n\n"
            else:
                context_with_video_ids += "\n"

        formatted_prompt = self.prompt_template.format(
            context=context_with_video_ids,
            query=query,
        )
        response = self.llm.invoke(formatted_prompt)
        return response.content

def create_dummy_vectorstore():
    print("Initializing embedding model...")
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("Creating dummy documents...")
    dummy_docs = [
        Document(page_content="Insulin is a hormone that regulates blood sugar.", metadata={"videoId": "abc123"}),
        Document(page_content="Type 2 diabetes is characterized by insulin resistance.", metadata={"videoId": "def456"}),
        Document(page_content="Exercise helps reduce insulin resistance.", metadata={"videoId": "ghi789"})
    ]
    print("Building FAISS index...")
    vectorstore = FAISS.from_documents(dummy_docs, embedding=embedding_model)
    
    print("FAISS index created.")
    return vectorstore
    
print("inside main")
vectorstore = create_dummy_vectorstore()
print("vector store created")

llm = HuggingFaceLLM(model_id="google/gemma-2b")
print("llm initialised")

prompt_template = """You are a helpful medical assistant.
Use the following context to answer the question.
{context}

Question: {query}
Answer:"""
print(prompt_template)

rag = RAGPipeline(
    vectorstore=vectorstore,
    embedding_model=None, 
         llm_model=llm,
         prompt_template_str=prompt_template
)

query = "What helps with insulin resistance?"
response = rag.generate_rag_response(query)
print("\n>>> RAG Response:\n", response)