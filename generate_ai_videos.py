import os
import time
from google import genai
from google.genai import types

def generate_video(prompt: str, filename: str):
    api_key = os.environ["GOOGLE_API_KEY"]

    client = genai.Client(api_key=api_key)

    operation = client.models.generate_videos(
        model="veo-3.0-generate-preview",
        prompt=prompt,
        config=types.GenerateVideosConfig(
            person_generation="allow_all",
            aspect_ratio="16:9",
            number_of_videos=1,
        ),
    )

    while not operation.done:
        time.sleep(20)
        operation = client.operations.get(operation)

    for n, generated_video in enumerate(operation.response.generated_videos):
        client.files.download(file=generated_video.video)
        generated_video.video.save(filename)

# Realistic AI transformation prompts (8 sectors)
prompts = [
    # 1. Healthcare
    "In a modern hospital, an AI-assisted robotic arm performs a minimally invasive surgery while one doctor oversee it through real-time feedback on screen, other doctor monitoring and and updating something on tab. Clean lighting, 1 doctor assisting the robotic arm ",

    # 2. Agriculture
    "On indian rural farm, solar-powered sensors collect soil data while AI-controlled sprinklers adjust irrigation. A farmer checks crop health on a tablet. Wide-angle sunrise shot, couple of drones fly-over the field. ",

    # 3. Finance
    "Inside a fintech office, a young analyst watches and updates the configuration on a screen, and watches AI-driven charts predicting market trends. as the Fast camera zoom-in on the green candlestick spike, that flashes the dramatic trading robot executes multiple orders, and the screen updates dramatically ",

    # 4. Retail
    "A customer walks into a Zudio retail store, greeted by a screen that personalizes recommendations based on face recognition. They try clothes using a smart mirror. Camera follows through aisle transitions and ends with a drone delivery outside the store.",

    # 5. Education
    # "In a futuristic classroom, students use AR glasses to visualize molecules and historical battles. A student practices coding using an AI mentor. Steady cam across students’ expressions, ending on a wide shot of a hybrid digital board.",

    # 6. Military
    "A command center monitors AI-powered drones scanning a desert region. Tactical alerts appear on-screen. Soldiers train with AI-simulated AR goggles. Scene cuts between drone feed and officer commands with a tilt shift focus.",

    # 7. Home Automation
    "A teenager enters a smart home through the door with retina scan,  coffee starts brewing dramatically, and zooms on fridge, where grocery list is prepared, ending with her smile as TV gets switched on.",

    # 8. Criminology
    "Backdrop mumbai city, CCTV system flags suspicious behavior in real-time. Police act before a crime occurs using AI heatmaps and facial recognition. Dark street scene cuts to control room with blinking alerts, then to officers intervening just in time."
]

# Generate videos from prompts
for i, prompt in enumerate(prompts, start=1):
    filename = f"ai_video_{i}.mp4"
    print(f"Generating video {i}: {filename}")
    generate_video(prompt, filename)
    print(f"Saved {filename}\n")