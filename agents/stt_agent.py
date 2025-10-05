# In agents/stt_agent.py

import io
import wave
import streamlit as st
import numpy as np
import whisper

# Load the base Whisper model once and cache it for performance
@st.cache_resource
def load_whisper_model(model_name="base"):
    # Using a smaller model like 'base.en' or 'tiny.en' is better for speed in a hackathon
    return whisper.load_model(model_name)

def process_audio_callback(audio_data):
    """
    Callback function that receives audio data chunks and processes them.
    This function is run in a background thread by streamlit-webrtc.
    """
    # 1. Load the model
    model = load_whisper_model("base") 
    
    # 2. Get the raw audio array (Mono, 16000Hz expected by Whisper)
    audio_buffer = audio_data.to_ndarray(format="s16", channels=1)
    
    # 3. Save the audio to a temporary in-memory WAV file (easier for Whisper)
    # Note: Using an in-memory stream is better than writing to disk in Docker
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) # 16-bit audio
        wf.setframerate(audio_data.sample_rate)
        wf.writeframes(audio_buffer.tobytes())
    wav_io.seek(0)
    
    # 4. Whisper Transcription
    try:
        # Whisper requires a file path or file-like object
        result = model.transcribe(wav_io)
        transcribed_text = result["text"]
    except Exception as e:
        # Fallback if transcription fails
        transcribed_text = f"Transcription Error: {e}" 

    # 5. Update the Streamlit state for the main thread to read
    st.session_state.stt_result = transcribed_text
    st.session_state.transcription_completed = True