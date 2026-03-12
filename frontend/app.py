import streamlit as st
import requests
import pandas as pd
import json

# -----------------------------
# Backend URL (local)
# -----------------------------
BACKEND_URL = "http://127.0.0.1:8000"

# -----------------------------
# Streamlit page config
# -----------------------------
st.set_page_config(page_title="Meeting Summarizer", layout="wide")
st.title("🎙 Meeting Summarizer AI")

# -----------------------------
# File uploader
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload an audio or video file",
    type=["wav", "mp3", "mp4"]
)

# -----------------------------
# Upload & Summarize
# -----------------------------
if st.button("Upload & Summarize"):

    if not uploaded_file:
        st.warning("Please upload a file before summarizing!")
        st.stop()

    st.audio(uploaded_file)

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type
        )
    }

    try:

        with st.spinner("Processing meeting..."):

            response = requests.post(
                f"{BACKEND_URL}/summarize",
                files=files,
                timeout=600
            )

        if response.status_code != 200:
            st.error("Backend error occurred.")
            st.code(response.text)
            st.stop()

        result = response.json()

        # -----------------------------
        # Display Results
        # -----------------------------
        st.subheader("📝 Summary")
        st.write(result.get("summary", "No summary available."))

        st.subheader("📄 Transcript")
        st.text_area(
            "Full Transcript",
            result.get("transcript", ""),
            height=300
        )

        st.subheader("🗣 Speakers")
        speakers = result.get("speakers", [])
        if speakers:
            st.dataframe(pd.DataFrame(speakers))
        else:
            st.info("No speaker data available.")

        st.subheader("📌 Action Items")
        actions = result.get("action_items", [])
        if actions:
            st.dataframe(pd.DataFrame(actions))
        else:
            st.info("No action items found.")

        st.subheader("❓ Key Questions")
        questions = result.get("key_questions", [])
        if questions:
            st.dataframe(pd.DataFrame(questions))
        else:
            st.info("No key questions found.")

        # -----------------------------
        # Download Report
        # -----------------------------
        st.subheader("⬇ Download Report")

        json_data = json.dumps(result, indent=4)

        st.download_button(
            "Download Full Report (JSON)",
            data=json_data,
            file_name="meeting_summary.json",
            mime="application/json"
        )

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Make sure FastAPI is running.")

    except requests.exceptions.Timeout:
        st.error("Request timed out. The meeting file may be too large.")

    except Exception as e:
        st.error("Unexpected error occurred.")
        st.code(str(e))