from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.youtubetranscript.helpers import get_top_video_details, get_transcript_text

# Create your views here.
class FetchTranscriptView(APIView):
    """View: Fetches Youtube transcript data"""

    def get(self, request):
        query = request.query_params.get('query', None)

        if query == None: return Response({"message": "Query is required."}, status.HTTP_400_BAD_REQUEST)
        
        function_status, return_details = get_top_video_details(query)

        if not function_status:
            return Response({"message": return_details, "results":[]}, status.HTTP_400_BAD_REQUEST)

        return_data = []
        indexer = 1

        for video_id, video_name in return_details:
            transcript = get_transcript_text(video_id)
            if transcript:
                return_data.append({"index":indexer, "video_name":video_name, "transcript":transcript})
            if len(return_data)==10: break
            indexer += 1

        return Response({"message": "Transcripts retrieved successfully.", "results": return_data}, status.HTTP_200_OK)
