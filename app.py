import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"   # Change later if backend is deployed

st.set_page_config(page_title="Voice-to-ABA Logger", layout="wide")
st.title("🎙️ Voice-to-ABA Logger")
st.write("Upload, record, or enter notes manually. Export all logs to CSV.")

# --- 1. Add Note Manually ---
st.header("✍️ Add Note Manually")
with st.form("manual_note"):
    student_name = st.text_input("Student Name")
    antecedent = st.text_input("Antecedent")
    behavior = st.text_input("Behavior")
    consequence = st.text_input("Consequence")
    submitted = st.form_submit_button("Save Note")

    if submitted:
        note = {
            "student_name": student_name,
            "antecedent": antecedent,
            "behavior": behavior,
            "consequence": consequence,
        }
        response = requests.post(f"{API_URL}/notes/", json=note)
        if response.status_code == 200:
            st.success("✅ Note added")
        else:
            st.error("❌ Failed to add note")


# --- 2. Transcribe Options ---
st.header("🎤 Transcribe Audio")

# Upload
audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])

# Sample
if st.button("Use Sample Recording"):
    with open("examples/sample_audio.wav", "rb") as f:   # <-- put a sample file in ./examples/
        files = {"file": ("sample_audio.wav", f, "audio/wav")}
        response = requests.post(f"{API_URL}/transcribe/", files=files)
        if response.status_code == 200:
            data = response.json()
            st.success("✅ Sample transcription complete!")
            st.json(data)
        else:
            st.error(f"Error: {response.text}")

# Upload transcription
if audio_file is not None and st.button("Transcribe Uploaded File"):
    files = {"file": (audio_file.name, audio_file, audio_file.type)}
    response = requests.post(f"{API_URL}/transcribe/", files=files)
    if response.status_code == 200:
        data = response.json()
        st.success("✅ Transcription complete!")
        st.json(data)
    else:
        st.error(f"Error: {response.text}")


# --- 3. Notes Table ---
st.header("📋 Notes Database")
if st.button("Refresh Notes"):
    response = requests.get(f"{API_URL}/notes/")
    if response.status_code == 200:
        notes = response.json().get("notes", [])
        if notes:
            df = pd.DataFrame(notes)
            st.dataframe(df)
        else:
            st.info("No notes found yet.")
    else:
        st.error("Failed to load notes.")


# --- 4. Export CSV ---
st.header("⬇️ Export Data")
if st.button("Download CSV"):
    response = requests.get(f"{API_URL}/export/")
    if response.status_code == 200:
        with open("notes_export.csv", "wb") as f:
            f.write(response.content)
        st.success("✅ CSV exported! Check notes_export.csv")
    else:
        st.error("Export failed.")
