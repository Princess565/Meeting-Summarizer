import streamlit as st
import requests
import pandas as pd
import json

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Meeting Summarizer", layout="wide")

st.title("🎙 Meeting Summarizer AI")

uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=["wav", "mp3"]
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

        # -------------------------
        # Loading Progress UI
        # -------------------------
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text("Uploading file...")
            progress_bar.progress(20)

            response = requests.post(
                f"{BACKEND_URL}/summarize",
                files=files,
                timeout=300
            )

            progress_bar.progress(60)
            status_text.text("Processing with AI...")

            if response.status_code == 200:

                result = response.json()

                progress_bar.progress(100)
                status_text.text("Completed ✅")

                # -------------------
                # Summary Section
                # -------------------
                st.subheader("📝 Summary")
                summary_text = result.get("summary", "No summary generated.")
                st.write(summary_text)

                # -------------------
                # Speaker Labels
                # -------------------
                st.subheader("🗣 Speakers")

                speakers = result.get("speakers", [])

                if speakers:
                    df_speakers = pd.DataFrame(speakers)
                    st.dataframe(df_speakers, use_container_width=True)
                else:
                    st.info("No speaker data available.")

                # -------------------
                # Action Items
                # -------------------
                st.subheader("📌 Action Items")

                action_items = result.get("action_items", [])

                if action_items:
                    df_actions = pd.DataFrame(action_items)
                    st.dataframe(df_actions, use_container_width=True)
                else:
                    st.info("No action items found.")

                # -------------------
                # Key Questions
                # -------------------
                st.subheader("❓ Key Questions")

                key_questions = result.get("key_questions", [])

                if key_questions:
                    df_questions = pd.DataFrame(key_questions)
                    st.dataframe(df_questions, use_container_width=True)
                else:
                    st.info("No key questions found.")

                # -------------------
                # Download Section
                # -------------------
                st.subheader("⬇ Download Results")

                # Download full JSON
                json_data = json.dumps(result, indent=4)

                st.download_button(
                    label="Download Full Report (JSON)",
                    data=json_data,
                    file_name="meeting_summary.json",
                    mime="application/json"
                )

                # Download Summary as Text
                st.download_button(
                    label="Download Summary (TXT)",
                    data=summary_text,
                    file_name="meeting_summary.txt",
                    mime="text/plain"
                )

            else:
                progress_bar.progress(100)
                status_text.text("Error ❌")
                st.error("Backend Error")
                st.text(response.text)

        except requests.exceptions.RequestException as e:
            progress_bar.progress(100)
            status_text.text("Connection Failed ❌")
            st.error("Connection Error")
            st.text(str(e))
            # -------------------
# Transcript Section
# -------------------
st.subheader("📄 Full Transcript")

transcript = result.get("transcript", "")

if transcript:
    st.text_area("Transcript", transcript, height=300)
else:
    st.info("No transcript available.")