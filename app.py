# app.py
import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="ABA Logger", layout="wide")

st.title("📘 ABA Logger Dashboard")

# --- Backend API helpers ---
def fetch_notes():
    try:
        res = requests.get(f"{API_URL}/notes/")
        res.raise_for_status()
        return res.json()["notes"]
    except Exception as e:
        st.error(f"Error fetching notes: {e}")
        return []

def delete_note(note_id):
    requests.delete(f"{API_URL}/notes/{note_id}")

def update_note(note_id, data):
    requests.put(f"{API_URL}/notes/{note_id}", json=data)

def add_note(data):
    requests.post(f"{API_URL}/notes/", json=data)

def export_notes():
    res = requests.get(f"{API_URL}/export/")
    if res.status_code == 200:
        st.download_button(
            label="⬇️ Download Exported CSV",
            data=res.content,
            file_name="notes_export.csv",
            mime="text/csv"
        )
    else:
        st.error(f"Export failed: {res.text}")

def transcribe_audio(file, student_name="Unknown"):
    files = {"file": (file.name, file, file.type)}
    res = requests.post(f"{API_URL}/transcribe/", files=files, params={"student_name": student_name})
    if res.status_code == 200:
        data = res.json()
        # Save into DB with student name
        add_note({
            "student_name": student_name,
            "antecedent": data.get("antecedent", ""),
            "behavior": data.get("behavior", ""),
            "consequence": data.get("consequence", ""),
        })
        return data
    else:
        st.error(f"Transcription failed: {res.text}")
        return None

# --- UI Sections ---

# Add new note manually
st.header("➕ Add a New Note")
with st.form("add_note_form"):
    student = st.text_input("Student Name")
    antecedent = st.text_area("Antecedent")
    behavior = st.text_area("Behavior")
    consequence = st.text_area("Consequence")
    # Removed timestamp input as DB handles it

    if st.form_submit_button("Save"):
        add_note({
            "student_name": student,
            "antecedent": antecedent,
            "behavior": behavior,
            "consequence": consequence,
        })
        st.success("Note added successfully")
        st.rerun()

# Audio transcription
st.header("🎙️ Upload Audio for Transcription")
student_for_audio = st.text_input("Student Name (for audio note)", "Unknown")
audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])

if st.button("Transcribe & Save") and audio_file:
    data = transcribe_audio(audio_file, student_for_audio)
    if data:
        st.success("Audio transcribed and saved as note")
        st.json(data)
        st.rerun()

# Show notes
st.header("📑 All Notes")
notes = fetch_notes()

if notes:
    df = pd.DataFrame(notes)
    st.dataframe(df, use_container_width=True)

    for note in notes:
        with st.expander(f"✏️ Edit Note {note['id']} - {note['student_name']}"):
            new_student = st.text_input("Student", value=note["student_name"], key=f"s{note['id']}")
            new_antecedent = st.text_area("Antecedent", value=note["antecedent"], key=f"a{note['id']}")
            new_behavior = st.text_area("Behavior", value=note["behavior"], key=f"b{note['id']}")
            new_consequence = st.text_area("Consequence", value=note["consequence"], key=f"c{note['id']}")
            # Removed timestamp edit as DB handles it

            col1, col2 = st.columns(2)
            if col1.button("💾 Save Changes", key=f"save{note['id']}"):
                update_note(note["id"], {
                    "student_name": new_student,
                    "antecedent": new_antecedent,
                    "behavior": new_behavior,
                    "consequence": new_consequence,
                })
                st.success(f"Note {note['id']} updated")
                st.rerun()
            if col2.button("🗑️ Delete Note", key=f"del{note['id']}"):
                delete_note(note["id"])
                st.warning(f"Note {note['id']} deleted")
                st.rerun()

else:
    st.info("No notes yet. Add one above.")

# Export CSV
if st.button("⬇️ Export Notes as CSV"):
    export_notes()