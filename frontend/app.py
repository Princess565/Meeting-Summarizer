import streamlit as st
import requests
import pandas as pd
import json

# 🔥 Live Render Backend
BACKEND_URL = BACKEND_URL = "http://backend:8000"

st.set_page_config(page_title="Meeting Summarizer", layout="wide")

st.title("🎙 Meeting Summarizer AI")

uploaded_file = st.file_uploader(
    "Upload an audio or video file",
    type=["wav", "mp3", "mp4"]
)

if uploaded_file:

    st.audio(uploaded_file)

    if st.button("Upload & Summarize"):

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        }

        progress = st.progress(0)
        status = st.empty()

        try:
            status.text("Sending file to backend...")
            progress.progress(30)

            response = requests.post(
                f"{BACKEND_URL}/summarize",
                files=files,
                timeout=600
            )

            progress.progress(70)
            status.text("Waiting for AI response...")

            progress.progress(100)

            # If backend failed, show full error
            if response.status_code != 200:
                st.error("Backend Error ❌")
                st.write("Status Code:", response.status_code)
                st.code(response.text)
                st.stop()

            result = response.json()

            status.text("Completed ✅")

            # Summary
            st.subheader("📝 Summary")
            st.write(result.get("summary", ""))

            # Transcript
            st.subheader("📄 Transcript")
            st.text_area(
                "Full Transcript",
                result.get("transcript", ""),
                height=300
            )

            # Speakers
            st.subheader("🗣 Speakers")
            speakers = result.get("speakers", [])
            if speakers:
                st.dataframe(pd.DataFrame(speakers))
            else:
                st.info("No speaker data available.")

            # Action Items
            st.subheader("📌 Action Items")
            actions = result.get("action_items", [])
            if actions:
                st.dataframe(pd.DataFrame(actions))
            else:
                st.info("No action items found.")

            # Key Questions
            st.subheader("❓ Key Questions")
            questions = result.get("key_questions", [])
            if questions:
                st.dataframe(pd.DataFrame(questions))
            else:
                st.info("No key questions found.")

            # Download JSON
            st.subheader("⬇ Download Report")

            json_data = json.dumps(result, indent=4)

            st.download_button(
                "Download Full Report (JSON)",
                data=json_data,
                file_name="meeting_summary.json",
                mime="application/json"
            )

        except requests.exceptions.Timeout:
            st.error("Request timed out. The backend took too long.")

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Check Render deployment.")

        except Exception as e:
            st.error("Unexpected error occurred.")
            st.code(str(e))