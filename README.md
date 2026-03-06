🎙 AI Meeting Summarizer

An AI-powered application that transcribes, analyzes, and summarizes meeting audio automatically.
The system extracts key insights from conversations including summaries, action items, key questions, and speaker segments.

Built using FastAPI, Whisper, Streamlit, and Gemini AI.

🚀 Features

✅ Upload meeting audio or video
✅ Automatic speech-to-text transcription
✅ AI-generated meeting summary
✅ Extract action items
✅ Detect key questions asked during meetings
✅ Display speaker segments
✅ Download results as TXT or JSON
✅ Clean API backend with FastAPI
✅ Interactive Streamlit web interface

🧠 Tech Stack

Backend

FastAPI – API framework

OpenAI Whisper – Speech-to-text transcription

FFmpeg – Audio extraction

Google Gemini – AI summarization

Frontend

Streamlit – Web interface

Language

Python

🏗 Project Architecture
Meeting-Summarizer
│
├── backend
│   ├── main.py
│   ├── uploads/
│   ├── requirements.txt
│   └── .env
│
├── frontend
│   └── app.py
│
├── .gitignore
└── README.md
⚙️ Installation
1️⃣ Clone the Repository
git clone https://github.com/YOUR_USERNAME/meeting-summarizer.git

cd meeting-summarizer
2️⃣ Create Virtual Environment
python -m venv venv

Activate:

Windows

venv\Scripts\activate

Mac / Linux

source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Install FFmpeg

This project requires FFmpeg for audio extraction.

Install from:

👉 https://ffmpeg.org/download.html

Verify installation:

ffmpeg -version
🔑 Environment Variables

Create a .env file inside the backend folder.

GEMINI_API_KEY=your_api_key_here

Get your API key from:

👉 Google AI Studio

▶ Running the Backend

Navigate to the backend folder:

cd backend

Run the API:

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

API documentation:

http://127.0.0.1:8000/docs
▶ Running the Frontend

Open a new terminal:

cd frontend

Run Streamlit:

streamlit run app.py

App will open in your browser:

http://localhost:8501
🧪 API Endpoint
POST /summarize

Upload meeting audio/video for analysis.

Response

{
  "summary": "...",
  "action_items": [],
  "key_questions": [],
  "transcript": "...",
  "speakers": []
}
📥 Example Output
Summary
The meeting discussed product roadmap updates and marketing strategy.
Action Items
Task	Speaker	Timestamp
Prepare marketing campaign	Sarah	00:12:32
Key Questions
Question	Speaker	Timestamp
When will the product launch?	John	00:05:21
📦 Deployment Ready

The backend is optimized for cloud deployment with:

Lightweight Whisper tiny model

Clean FastAPI architecture

Health check endpoint

GET /health

Returns:

{
  "status": "ok"
}
🔮 Future Improvements

Speaker diarization

Real-time meeting transcription

Meeting sentiment analysis

Automatic calendar integration

Slack / Teams integration

Multi-language transcription

👨‍💻 Author

Efe Ikharo

Biomedical Scientist transitioning into AI & Data Science.

LinkedIn
https://www.linkedin.com/in/efeikharo/

⭐ If You Like This Project

Give it a ⭐ on GitHub!