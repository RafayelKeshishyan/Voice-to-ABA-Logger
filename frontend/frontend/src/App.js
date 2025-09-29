import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

function App() {
  const [student, setStudent] = useState("Student A");
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(false);

  const audioRef = useRef();

  // Fetch stored notes
  const fetchNotes = async () => {
    const res = await axios.get("http://localhost:8000/notes/");
    setNotes(res.data.notes);
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  // Start Recording
  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    let chunks = [];

    recorder.ondataavailable = (e) => chunks.push(e.data);
    recorder.onstop = () => {
      const blob = new Blob(chunks, { type: "audio/wav" });
      setAudioBlob(blob);
      if (audioRef.current) {
        audioRef.current.src = URL.createObjectURL(blob);
      }
      chunks = [];
    };

    recorder.start();
    setMediaRecorder(recorder);
    setRecording(true);
  };

  // Stop Recording
  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setRecording(false);
    }
  };

  // Send audio to backend
  const handleTranscribe = async () => {
    if (!audioBlob) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.wav");

    const res = await axios.post("http://localhost:8000/transcribe/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    alert("Transcribed:\n" + res.data.transcription);
    fetchNotes();
    setLoading(false);
  };

  // Export notes
  const handleExport = async () => {
    const res = await fetch("http://localhost:8000/export/");
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "notes_export.csv";
    link.click();
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-6">🎤 ABA Logger</h1>

      {/* Student Dropdown */}
      <div className="mb-4">
        <label className="mr-2 font-semibold">Student:</label>
        <select
          value={student}
          onChange={(e) => setStudent(e.target.value)}
          className="p-2 border rounded"
        >
          <option>Student A</option>
          <option>Student B</option>
          <option>Student C</option>
        </select>
      </div>

      {/* Recording Controls */}
      <div className="flex gap-3 mb-4">
        {!recording ? (
          <button
            onClick={startRecording}
            className="px-4 py-2 bg-green-500 text-white rounded"
          >
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="px-4 py-2 bg-red-500 text-white rounded"
          >
            Stop Recording
          </button>
        )}
        <button
          onClick={handleTranscribe}
          disabled={!audioBlob || loading}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
        >
          {loading ? "Processing..." : "Transcribe & Save"}
        </button>
      </div>

      {/* Audio Preview */}
      {audioBlob && <audio ref={audioRef} controls className="mb-4" />}

      {/* Notes Table */}
      <h2 className="text-xl font-semibold mb-2">Saved Notes</h2>
      <table className="w-full bg-white border rounded shadow">
        <thead>
          <tr className="bg-gray-200">
            <th className="p-2 border">Student</th>
            <th className="p-2 border">Antecedent</th>
            <th className="p-2 border">Behavior</th>
            <th className="p-2 border">Consequence</th>
            <th className="p-2 border">Time</th>
          </tr>
        </thead>
        <tbody>
          {notes.map((note) => (
            <tr key={note.id} className="text-center">
              <td className="p-2 border">{note.student_name}</td>
              <td className="p-2 border">{note.antecedent}</td>
              <td className="p-2 border">{note.behavior}</td>
              <td className="p-2 border">{note.consequence}</td>
              <td className="p-2 border">{note.timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Export */}
      <button
        onClick={handleExport}
        className="mt-4 px-4 py-2 bg-purple-500 text-white rounded"
      >
        Export as CSV
      </button>
    </div>
  );
}

export default App;
