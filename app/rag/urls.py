from django.urls import path

from app.rag.views import rag_query

urlpatterns = [
    path("query/", rag_query, name="rag_query"),
  ]