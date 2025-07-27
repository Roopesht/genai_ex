
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from create_video import generate_video

def upload_video(file_path, title, description, tags, thumbnail_path) -> str:
    # Authenticate
    """prompt = Create a 30–60 second lifestyle video ad for a brand selling trendy handbags for college students.

Structure:
	1.	Opening Shot (3–5 sec):
	•	Close-up of two chic, colorful handbags on a stylish desk or in a dorm room with natural lighting.
	•	On-screen text: “Meet Your Campus BFFs 💼✨”
	2.	Middle (15–30 sec):
	•	Show a diverse group of college girls walking across campus, laughing, going to the library, or hanging out in a café — each with one of the handbags.
	•	Include quick transitions showing the bags being opened to hold laptops, makeup, books.
	•	Highlight comfort, style, and storage space in action.
	3.	Ending (5–10 sec):
	•	Bag placed on a library table, girl smiles at the camera.
	•	On-screen CTA: “Style that speaks. Shop now at www.trendybagscollege.com”
    """
    #generate_video(prompt,file_path )
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "/etc/secrets/client_secret.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=8000)
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    # Upload request
    request_body = {
        "snippet": {
            "categoryId": "24",
            "title": title,
            "description": description ,
            "tags": tags
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media_file = googleapiclient.http.MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/*")

    request = youtube.videos().insert(
        
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )
    try:
        response = request.execute()
        id = response['id']
        print("Video uploaded. Video ID:", id)
        return f"https://youtu.be/{id}"
    except Exception as e:
        print ("Could not upload: ", e)
        return ""
    # Upload thumbnail
# Example Usage
"""
upload_video(
    file_path="video.mp4",
    title="Trendy Handbags for College Students 🎒✨ | Must-Have Campus Styles",
    description="Discover the trendiest bags every college girl needs. Light, stylish, and built for campus life.",
    tags=["trendy handbags", "college accessories", "fashion bags", "campus fashion"],
    thumbnail_path="thumbnail.jpg"
)
"""
