import os
import time
import requests
from google import genai
from google.genai import types
import jwt


import os
import time
import hmac
import hashlib
import base64
import requests

def authenticate():
    """
    Generate a JWT token using KLING_ACCESS_KEY and KLING_SECRET_KEY.
    """
    access_key = os.getenv("KLING_ACCESS_KEY")
    secret_key = os.getenv("KLING_SECRET_KEY")

    if not access_key or not secret_key:
        raise EnvironmentError("❌ Missing KLING_ACCESS_KEY or KLING_SECRET_KEY in environment variables.")

    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": access_key,
        "exp": int(time.time()) + 1800,  # Token valid for 30 minutes
        "nbf": int(time.time()) - 5      # Effective 5 seconds ago
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256", headers=headers)
    return token if isinstance(token, str) else token.decode("utf-8")


def generate_video_kling(prompt: str, filename: str, style="realistic", resolution="720p"):
    """
    Generate video using KlingAI /v1/videos/text2video API.
    """
    # Step 1: Authenticate and get JWT token
    api_token = authenticate()
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    

    # Step 2: Task Creation
    base_url = "https://api-singapore.klingai.com"
    create_url: str = f"{base_url}/v1/videos/text2video"
    body = {
        "prompt": prompt,
        "model_name": "kling-v1",         # safe default
        "duration": "5",                  # enum: "5" or "10"
        "aspect_ratio": "16:9",           # enum
        "mode": "std"
    }

    response = requests.post(create_url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(f"❌ Error creating video task: {response.status_code} - {response.text}")

    task = response.json()
    task_id = task.get("data", {}).get("task_id")
    if not task_id:
        raise Exception("❌ No task_id returned from Kling API.")

    print(f"📤 Task created: {task_id} — generating video...")

    # Step 3: Polling Task Status
    status_url = f"{base_url}/v1/videos/text2video/{task_id}"
    video_url = None

    for attempt in range(240):  # Wait up to 3 minutes
        time.sleep(5)
        status_resp = requests.get(status_url, headers=headers)
        if status_resp.status_code != 200:
            print(f"⚠️ Polling failed: {status_resp.status_code}")
            continue

        status_json = status_resp.json()
        status = status_json.get("data").get("task_status")

        if status == "succeed":
            video_url = status_json.get("data").get("task_result").get("videos")[0].get("url")
            print(f"✅ Video ready: {video_url}")
            break
        elif status == "failed":
            raise Exception("❌ Video generation failed.")
        else:
            print(f"⏳ Status: {status}...")

    if not video_url:
        raise TimeoutError("⏱️ Video generation timed out after multiple retries.")

    # Step 4: Download Video
    video_response = requests.get(video_url)
    with open(filename, "wb") as f:
        f.write(video_response.content)

    print(f"🎬 Video saved to {filename}")

def generate_image_vyro(
    prompt: str,
    filename: str,
    style="realistic",
    aspect_ratio="1:1",
    seed="5",
    api_key=None
):
    """Generate image using Vyro API (direct image download)."""
    if api_key is None:
        api_key = os.getenv("IMAGINE_KEY")

    url = "https://api.vyro.ai/v2/image/generations"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    files = {
        "prompt": (None, prompt),
        "style": (None, style),
        "aspect_ratio": (None, aspect_ratio),
        "seed": (None, seed),
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code != 200:
        print("❌ API returned non-200 response.")
        print(f"Status: {response.status_code}")
        print("Content:")
        print(response.content.decode("utf-8", errors="ignore"))
        raise Exception("Image generation failed.")

    # ✅ Directly save image content
    with open(filename, "wb") as f:
        f.write(response.content)

    print(f"🖼️ Image saved directly to {filename}")

def generate_video_vyro(prompt: str, filename: str, style="kling-1.0-pro", api_key=None):
    """Generate video using Vyro API with multipart/form-data."""
    if api_key is None:
        api_key = os.getenv("IMAGINE_KEY")

    url = "https://api.vyro.ai/v2/video/text-to-video"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # Using files to force multipart/form-data content-type
    files = {
        "style": (None, style),
        "prompt": (None, prompt)
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code != 200:
        raise Exception(f"Vyro API error: {response.status_code} - {response.text}")

    result = response.json()
    video_url = result.get("video_url") or result.get("url")

    if not video_url:
        raise Exception("Video URL not found in response")

    # Download the video content
    video_response = requests.get(video_url)
    with open(filename, "wb") as f:
        f.write(video_response.content)

    print(f"✅ Video saved as {filename}")

def generate_video_veo(prompt: str, filename: str, model="veo-3.0-generate-preview"):
    """Generate video using Google Veo API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)

    operation = client.models.generate_videos(
        model=model,
        prompt=prompt,
        config=types.GenerateVideosConfig(
            person_generation="allow_all",
            aspect_ratio="16:9",
            number_of_videos=1
        ),
    )

    while not operation.done:
        print("⏳ Waiting for video generation...")
        time.sleep(20)
        operation = client.operations.get(operation)

    for n, generated_video in enumerate(operation.response.generated_videos):
        client.files.download(file=generated_video.video)
        generated_video.video.save(filename)

    print(f"✅ Video saved as {filename}")


def generate_video(prompt: str, filename: str, provider: str = "vyro"):
    """
    Generate a video from text using the specified provider.

    :param prompt: Text prompt for video generation.
    :param filename: Output filename for the video.
    :param provider: 'vyro' or 'veo'
    """
    if provider == "vyro":
        generate_video_vyro(prompt, filename)
    elif provider == "veo":
        generate_video_veo(prompt, filename)
    else:
        raise ValueError("Invalid provider. Use 'vyro' or 'veo'.")


# Example usage
if __name__ == "__main__":
    prompt_text = "a flying dinosaur"
    output_file = "flying_dino.mp4"

    # Set VYRO_API_KEY or GOOGLE_API_KEY in environment variables
    generate_video(prompt=prompt_text, filename=output_file, provider="vyro")


    # Image generation using Vyro
    generate_image_vyro(
        prompt="A futuristic cityscape at night with neon lights",
        filename="futuristic_city.png"
    )