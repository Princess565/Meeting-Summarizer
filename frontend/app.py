import streamlit as st
import requests
import pandas as pd
import json

# 🔥 Your LIVE Render backend
BACKEND_URL = "https://five65-meeting-summarizer.onrender.com"

st.set_page_config(page_title="Meeting Summarizer", layout="wide")

st.title("🎙 Meeting Summarizer AI")

uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=["wav", "mp3", "mp4"]
)

if uploaded_file is not None:

    st.audio(uploaded_file)

    if st.button("Upload & Summarize"):

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        }

        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text("Uploading file...")
            progress_bar.progress(20)

            response = requests.post(
                f"{BACKEND_URL}/summarize",
                files=files,
                timeout=600
            )

            progress_bar.progress(60)
            status_text.text("Processing with AI...")

            if response.status_code == 200:

                result = response.json()

                progress_bar.progress(100)
                status_text.text("Completed ✅")

                # Summary
                st.subheader("📝 Summary")
                st.write(result.get("summary", ""))

                # Transcript
                st.subheader("📄 Full Transcript")
                st.text_area(
                    "Transcript",
                    result.get("transcript", ""),
                    height=300
                )

                # Speakers
                st.subheader("🗣 Speakers")
                speakers = result.get("speakers", [])
                if speakers:
                    st.dataframe(pd.DataFrame(speakers))

                # Action Items
                st.subheader("📌 Action Items")
                action_items = result.get("action_items", [])
                if action_items:
                    st.dataframe(pd.DataFrame(action_items))

                # Key Questions
                st.subheader("❓ Key Questions")
                key_questions = result.get("key_questions", [])
                if key_questions:
                    st.dataframe(pd.DataFrame(key_questions))

                # Download JSON
                st.subheader("⬇ Download Results")
                json_data = json.dumps(result, indent=4)

                st.download_button(
                    "Download Full Report (JSON)",
                    json_data,
                    "meeting_summary.json",
                    "application/json"
                )

            else:
                progress_bar.progress(100)
                status_text.text("Error ❌")
                st.error(response.text)

        except requests.exceptions.RequestException as e:
            progress_bar.progress(100)
            status_text.text("Connection Failed ❌")
            st.error(str(e))