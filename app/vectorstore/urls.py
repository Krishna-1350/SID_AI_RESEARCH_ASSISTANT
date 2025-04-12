from django.urls import path

from app.vectorstore.views import TranscriptRAGView

urlpatterns = [
    path('transcript-rag/', TranscriptRAGView.as_view(), name='transcript-rag'),
]