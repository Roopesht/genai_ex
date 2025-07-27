import os
import time
import openai
from nicegui import ui
from create_video import generate_video_kling
from upload_video import upload_video


class GenAIApp:

    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

        self.prompt_data: dict[str, str] = {
            'user_input': '',
            'product1': '',
            'product2': '',
            'prompt_output': '',
            'video_prompt': '',
            'video_url': '',
            'video_status': 'Not Started',
            'title':'',
            'description':''
        }
        self.user_input = None
        self.prompt_output = None
        self.video_status = None
        self.website_url = None

        self.build_ui()

    def get_openai_response(self, prompt: str, temperature=0.7, max_tokens=500):
        response = openai.ChatCompletion.create(
            model="gpt-4.1-nano", #"gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for creating business product websites and videos."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response['choices'][0]['message']['content'].strip()

    def build_ui(self):
        with ui.card().classes('w-full max-w-3xl mx-auto mt-10 shadow-lg p-6'):
            ui.label("🚀 GenAI: Business Idea → Website + Video").classes("text-3xl font-bold mb-6 text-center")

            with ui.card().classes("w-full p-4 border border-gray-300 rounded-lg shadow-sm"):
                with ui.row().classes("items-end w-full gap-4"):
                    self.user_input = ui.input(
                        label="📝 Raw Business Idea",
                        placeholder="e.g., I want to build an app for freelancers to share tasks"
                    ).props('id=user_input').classes("w-3/4")
                    ui.button("✨ Generate", on_click=self.generate).classes("bg-primary text-white w-1/5")

            with ui.card().classes("w-full p-4 border border-gray-300 rounded-lg shadow-sm"):
                with ui.row().classes("items-center justify-between mt-2"):
                    ui.label("🌐 Prompt to Generate Website").classes("font-semibold")
                    ui.button("", icon="content_copy", on_click=lambda: ui.run_javascript(
                        'navigator.clipboard.writeText(document.getElementById("prompt_output").value);'
                    )).props('dense').classes("text-xs")

                self.prompt_output = ui.textarea(
                    label="Prompt Output"
                ).props('id=prompt_output').classes("w-full")

                self.website_url = ui.input(
                    label="🔗 Website URL (used in video description)",
                    placeholder="https://yourbusiness.com"
                ).props('id=website_url').classes("w-full mt-4")

                ui.button("🎬 Create Product 1 Video", on_click=self.create_video).classes("mt-4 bg-pink-500 text-white")

            ui.label("📡 Status").classes("mt-6 text-sm font-medium text-gray-700")
            self.video_status = ui.input(self.prompt_data["video_status"]).props('readonly id=status_output').classes("text-md text-blue-700 w-full mt-4")

    def update_ui_with_js(self):
        self.prompt_output.set_value (self.prompt_data.get('prompt_output', ''))
        self.prompt_output.update()
        self.video_status.set_value (self.prompt_data.get('video_status', ''))
        self.video_status.update()

        #ui.run_javascript('window.location.reload();')
        """
        self.video_status.value = self.prompt_data.get('video_status', '')
        self.video_status.update()
        prompt_js = (
            f'document.getElementById("prompt_output").value = `{self.prompt_data.get("prompt_output", "")}`;'
        )
        ui.run_javascript(prompt_js)
        """

        

    def generate(self):
        self.prompt_data['video_status'] = "⚙️ Generating prompts..."

        idea = self.user_input.value

        if not idea:
            ui.notify("❗ Please enter a business idea.")
            return
        else:
            self.prompt_data['user_input'] = idea

        base_web_prompt = (
            f"You are helping build an e-commerce business website.\n"
            f"Business idea: {idea}\n\n"
            f"Suggest 2 product ideas.\n"
            f"Make Product 1 well-defined with purpose, features, and benefits. "
            f"Product 2 can be simpler.\n\n"
            f"Respond ONLY in this format:\n"
            f"Product 1:\n<detailed description>\n\nProduct 2:\n<brief description>"
        )

        try:
            product_details = self.get_openai_response(base_web_prompt)
            parts = product_details.split("Product 2:")
            product1 = parts[0].replace("Product 1:", "").strip()
            product2 = parts[1].strip()
        except Exception as e:
            ui.notify("❌ Error parsing product descriptions." + str(e))
            return

        self.prompt_data['product1'] = product1
        self.prompt_data['product2'] = product2

        final_web_prompt = (
            f"Create a responsive HTML/CSS/JS landing page for this business idea: {idea}\n\n"
            f"Showcase:\n\n"
            f"👉 Product 1 (highlighted with image placeholder and feature list):\n{product1}\n\n"
            f"👉 Product 2 (simple card-style layout):\n{product2}\n\n"
            f"Include 'Add to Cart' for both and a working cart."
        )

        self.prompt_data['prompt_output'] = final_web_prompt

        video_metadata_prompt = (
            f"You are a creative marketing assistant. Based on the product below, generate:\n"
            f"1. A short but powerful 5-second video script prompt (what to say, tone, how to open and close)\n"
            f"2. A catchy video **title** (max 60 characters)\n"
            f"3. A short **description** for the video (max 160 characters)\n\n"
            f"Product:\n{product1}\n\n"
            f"Respond in this JSON format:\n"
            f"{{\n"
            f"  \"video_prompt\": \"...\",\n"
            f"  \"title\": \"...\",\n"
            f"  \"description\": \"...\"\n"
            f"}}"
        )

        try:
            import json
            video_response_raw = self.get_openai_response(video_metadata_prompt)
            video_metadata = json.loads(video_response_raw)

            self.prompt_data['video_prompt'] = video_metadata['video_prompt']
            self.prompt_data['title'] = video_metadata['title']
            self.prompt_data['description'] = video_metadata['description']

        except Exception as e:
            ui.notify(f"❌ Error generating video metadata: {e}")
            return

        self.prompt_data['video_status'] = "✅ Prompt Generated"
        self.update_ui_with_js()

        ui.notify("✨ Products and prompts generated!")
    
    def create_video_kling(self):
        video_prompt = self.prompt_data['video_prompt']
        if not video_prompt:
            ui.notify("❗ Please generate the prompt first.")
            return

        filename = f"video_{int(time.time())}.mp4"
        self.prompt_data['video_status'] = "🎥 Generating video for Product 1..."
        self.update_ui_with_js()

        try:
            generate_video_kling(prompt=video_prompt, filename=filename)
        except Exception as e:
            self.prompt_data['video_status'] = f"❌ Video generation failed: {e}"
            self.update_ui_with_js()
            return

        self.prompt_data['video_status'] = "⬆️ Uploading video to YouTube..."
        self.update_ui_with_js()
        return filename

    def create_video(self):
        filename = self.create_video_kling()
        #filename = "video_1753593196.mp4"

        try:
            #url_text = ui.query('#website_url').props('value') or "https://yourwebsite.com"
            url = upload_video(
                file_path=filename,
                title=self.prompt_data['title'][:60],
                description=f"{self.prompt_data['description']}!\nVisit us: {self.website_url.value}",
                tags=["AI", "business", "video"],
                thumbnail_path=None
            )
            self.prompt_data['video_status'] = f'✅ Uploaded, url: {url}'
            ui.run_javascript('alert("Video uploaded successfully!");')
            # show javascript alert ('generated video');
            self.update_ui_with_js()
        except Exception as e:
            self.prompt_data['video_status'] = f'❌ Upload Failed: {e} - {traceback.format_exc()}'

        self.update_ui_with_js()


GenAIApp()
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="AI Video Generator",
        reload=False,
        port=8080,
        host="0.0.0.0"  # Render needs this to serve
    )
