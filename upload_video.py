import os
import pickle
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from create_video import generate_video
import base64

def encode_base64(input_file_path: str, output_file_path: str):
    """
    Encode a binary file to a base64-encoded text file.

    Args:
        input_file_path: Path to the binary input file (e.g., .pickle).
        output_file_path: Path to save the base64-encoded output file.
    """
    with open(input_file_path, "rb") as f_in:
        binary_data = f_in.read()
        encoded_data = base64.b64encode(binary_data)

    with open(output_file_path, "wb") as f_out:
        f_out.write(encoded_data)
    print(f"✅ Encoded base64 written to {output_file_path}")

def decode_base64(input_file_path: str, output_file_path: str):
    """
    Decode a base64-encoded text file back to its original binary form.

    Args:
        input_file_path: Path to the base64-encoded input file.
        output_file_path: Path to save the decoded binary file.
    """
    with open(input_file_path, "rb") as f_in:
        encoded_data = f_in.read()
        binary_data = base64.b64decode(encoded_data)

    with open(output_file_path, "wb") as f_out:
        f_out.write(binary_data)
    print(f"✅ Decoded binary written to {output_file_path}")

def upload_video(file_path, title, description, tags, thumbnail_path) -> str:
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = os.getenv("CLIENT_SECRET_FILE")
    credentials_file = os.getenv("YOUTUBE_TOKEN_PICKLE_FILE")

    credentials = None
    
    if not credentials_file:
        raise ValueError("Missing environment variable: YOUTUBE_TOKEN_PICKLE_FILE")
    youtube_token_file = 'local_youtube_token.pickle'
    # Load credentials if already stored
    if os.path.exists(credentials_file, ):
        decode_base64(credentials_file, youtube_token_file)
        with open(youtube_token_file, 'rb') as token:
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
        with open(youtube_token_file, 'wb') as token:
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