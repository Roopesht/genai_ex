# 🚀 GenAI Utility: From Business Idea → Website + Video + YouTube Upload

**Unlock the power of GenAI** — Transform your business idea into a stunning product website, an engaging promo video, and a ready-to-publish YouTube upload — all effortlessly, in one seamless flow!


If you'd like to learn GenAI from the ground up, contact **Mr. Roopesh Tayaloor** by visiting [https://ojasamirai.com/training.html](https://ojasamirai.com/training.html).

---

## ✨ Features

1. **Input Raw Business Idea**
   → The app expands it into a full product definition.

2. **Generate Website Prompt**
   → For a landing page with:

   * Two products
   * Add-to-cart buttons
   * Responsive layout

3. **Auto-create Product Promo Video**
   → Uses **KlingAI** or **Google Veo** APIs based on prompt.

4. **Upload to YouTube**
   → Video is uploaded along with a generated **title**, **description**, and optional **website URL**.

---

## 🎞️ Project Structure

```
.
├── main.py                  # UI logic + workflow
├── create_video.py          # KlingAI / Vyro / Veo video generation
├── upload_video.py          # YouTube upload logic
├── README.md                # You are here
└── requirements.txt         # Python dependencies
```

---

## 🛠️ Setup Instructions

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/genai-idea-launcher.git
cd genai-idea-launcher
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file (or export manually):

```env
OPENAI_API_KEY=your_openai_key
KLING_ACCESS_KEY=your_kling_access_key
KLING_SECRET_KEY=your_kling_secret_key
GOOGLE_API_KEY=your_google_genai_api_key
CLIENT_SECRET_FILE=path_to_your_youtube_client_secret.json
YOUTUBE_TOKEN_PICKLE_FILE=base64_encoded_pickle_path.txt
```

> 🔐 The YouTube token file should be stored in **base64-encoded** format (see `upload_video.py` for helper methods).

### 3. Run the App

```bash
python main.py
```

Visit **[http://localhost:8080](http://localhost:8080)** in your browser.

---

## 🖼️ App Flow Summary

1. **Enter Business Idea**
2. Click **"Generate"**

   * Auto-generates 2 product definitions
   * Prepares website prompt
   * Creates 5-sec video script, title & description
3. Enter **Website URL**
4. Click **"Create Product 1 Video"**

   * Video is generated
   * Uploaded to YouTube
   * Status + YouTube URL is shown

---

## 📄 Video Generation

Supports the following providers (controlled in `create_video.py`):

| Provider   | API                       | Notes                |
| ---------- | ------------------------- | -------------------- |
| KlingAI    | `/v1/videos/text2video`   | JWT-authenticated    |
| Vyro       | `/v2/video/text-to-video` | API-key-based        |
| Google Veo | `genai.Client`            | Use `GOOGLE_API_KEY` |

> Default: **KlingAI**

---

## 📺 YouTube Upload

* OAuth flow handled via `upload_video.py`
* Requires:

  * `client_secret.json`
  * `pickle` token (stored in base64 format)
* Video metadata (title, description, tags) generated automatically

---

## 🥪 Sample Output

**Input:**
`I want to build an app for freelancers to share tasks`

**Output:**

* Product 1: Task Collaboration App
* Product 2: Freelancer Time Tracker
* Website HTML Prompt
* 5-sec Video Prompt: "Join the freelancer revolution..."
* Title: `Boost Your Freelance Productivity`
* Description: `Your all-in-one freelance toolkit – start now!`
* Uploaded to YouTube ✅

---

## 🔑 Tips for Deployment

* Run with `host='0.0.0.0'` for cloud (e.g., **Render**, **Docker**).
* Ensure ports `8080` (NiceGUI) and `8000` (YouTube OAuth) are open.
* Keep API keys & tokens secure using `.env` or secret managers.

---

## 📋 Requirements

```
nicegui
openai
requests
google-api-python-client
google-auth
google-auth-oauthlib
python-jose
```

Install via:

```bash
pip install -r requirements.txt
```

---

## 📙 Future Enhancements

* Add video preview before upload
* Switch between KlingAI/Vyro/Veo via UI dropdown
* Save generated HTML to file or publish via Netlify/Firebase
* Support multiple video durations/styles
* Analytics dashboard (views, traffic, etc.)

---

## 🙌 Acknowledgements

* [OpenAI](https://platform.openai.com/)
* [KlingAI](https://klingai.com/)
* [Google Veo (GenAI)](https://deepmind.google/technologies/veo/)
* [YouTube Data API](https://developers.google.com/youtube/registering_an_application)

---

## 📞 Contact

**Author**: Roopesh Kumar T P
📧 [training@ojasamirai.com](mailto:training@ojasamirai.com)
🌐 [ojasamirai.com](https://ojasamirai.com/training.html)
