# In agents/voice_agent.py

import os
import streamlit as st
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

# Initialize ElevenLabs client
try:
    eleven_client = ElevenLabs(api_key=ELEVEN_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize ElevenLabs client: {e}")
    eleven_client = None


def generate_and_play(text, voice_id, msg_id, speed_rate=1.0):
    """
    Generate and play audio using ElevenLabs old SDK structure.
    Compatible with v0.x versions (no .audio.generate).
    """
    if not eleven_client:
        st.error("ElevenLabs client not initialized.")
        return

    audio_file = f"tts_output_{msg_id}_{voice_id}.mp3"

    if not os.path.exists(audio_file):
        try:
            # OLD SDK endpoint expects arguments like this:
            response = eleven_client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                text=text,
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                },
            )

            # Save audio stream
            with open(audio_file, "wb") as f:
                for chunk in response:
                    if chunk:
                        f.write(chunk)

        except Exception as e:
            st.error(f"Error generating voice. Check your API key or plan. Details: {e}")
            return

    # Play the audio file
    with open(audio_file, "rb") as f:
        st.audio(f.read(), format="audio/mp3")
