import os
import pickle
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from create_video import generate_video

def upload_video(file_path, title, description, tags, thumbnail_path) -> str:
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = os.getenv("CLIENT_SECRET_FILE")
    credentials_file = os.getenv("YOUTUBE_TOKEN_PICKLE_FILE")

    credentials = None

    # Load credentials if already stored
    if os.path.exists(credentials_file):
        with open(credentials_file, 'rb') as token:
            credentials = pickle.load(token)

    # Refresh or create new credentials if needed
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes)
            credentials = flow.run_local_server(port=8000)
        # Save the credentials for next run
        with open(credentials_file, 'wb') as token:
            pickle.dump(credentials, token)

    # Build the YouTube API client
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    # Create the video metadata
    request_body = {
        "snippet": {
            "categoryId": "24",
            "title": title,
            "description": description,
            "tags": tags
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media_file = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/*")

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    try:
        response = request.execute()
        video_id = response.get('id')
        print("✅ Video uploaded. Video ID:", video_id)
        return f"https://youtu.be/{video_id}"
    except Exception as e:
        print("❌ Could not upload video:", e)
        return ""