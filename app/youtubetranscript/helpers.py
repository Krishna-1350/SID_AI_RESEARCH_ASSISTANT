from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth.exceptions
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

def get_top_video_details(query, max_results=30):
    api_key = settings.YOUTUBE_API_KEY

    try:
        youtube = build('youtube', 'v3', developerKey=api_key)

        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_results,
            videoCaption='closedCaption',
            relevanceLanguage='en',
            videoDuration='short',
            safeSearch='moderate',
            order='relevance',
        )
        response = request.execute()

        top_video_details = [(item['id']['videoId'], item['snippet']['title']) for item in response['items']]
        return True, top_video_details
    
    except HttpError as e:
        error_reason = ''
        if e.resp.status == 403:
            error_reason = 'Quota exceeded or API key is disabled.'
        elif e.resp.status == 400:
            error_reason = 'Bad request - possibly malformed or invalid API key.'
        else:
            error_reason = f'HTTP error occurred: {e}'

    except google.auth.exceptions.DefaultCredentialsError as e:
        error_reason = f"Authentication error: {e}"

    except Exception as e:
        error_reason = f"An unexpected error occurred: {e}"
    
    return False, error_reason

def get_transcript_text(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([x['text'] for x in transcript])
        return full_text
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

