from django.urls import path

from app.youtubetranscript.views import FetchTranscriptView

urlpatterns = [
    path('fetch-transcript/', FetchTranscriptView.as_view(), name='fetch-youtube-transcript'),
]