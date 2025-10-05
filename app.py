import streamlit as st
import os
from dotenv import load_dotenv
import urllib.parse

from cerebras.cloud.sdk import Cerebras
from exa_py import Exa
from elevenlabs.client import ElevenLabs



from agents.orchestrator import run_pipeline
from agents.voice_agent import generate_and_play

# --- Load environment variables ---
load_dotenv()

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

cb = Cerebras(api_key=CEREBRAS_API_KEY)
exa = Exa(api_key=EXA_API_KEY)
eleven_client = ElevenLabs(api_key=ELEVEN_API_KEY)

# --- Streamlit page setup ---
st.set_page_config(page_title="PolyVoice", layout="wide")

st.markdown(
    """
    <style>
        /* General app background (keep gray/dark) */
        .stApp {
            background-color: #111111 !important;
            color: white !important;
        }

        /* Title + subtitle */
        h1, p {
            text-align: center;
        }

        /* Text input + button alignment */
        .stTextInput > div > div > input {
            height: 3rem !important;
            border-radius: 8px !important;
            border: 1px solid #0078FF !important;
            background-color: #1a1a1a !important;
            color: white !important;
        }
        .stButton button {
            height: 3rem !important;
            width: 100% !important;
            border-radius: 8px !important;
            background-color: #0078FF !important;
            color: white !important;
            border: none !important;
            margin-top: 0.25rem !important;
            transition: background 0.3s ease !important;
        }
        .stButton button:hover {
            background-color: #005ecc !important;
        }

        /* Blue border on focus for source links */
        a:focus, a:active {
            border: 1px solid #0078FF !important;
            border-radius: 4px !important;
            padding: 2px 4px !important;
        }

        /* Chat bubbles */
        .user-bubble {
            background: #0078FF;
            color: white;
            padding: 10px 15px;
            border-radius: 15px;
            margin: 10px 0;
            width: fit-content;
            margin-left: auto;
            max-width: 85%;
        }

        .assistant-bubble {
            background: #222222;
            color: white;
            padding: 10px 15px;
            border-radius: 15px;
            margin: 10px 0;
            width: fit-content;
            margin-right: auto;
            max-width: 85%;
            text-align: left !important; /* ensure text is left aligned */
            margin-left: 0 !important;   /* stick to left side */
            margin-right: auto !important;
        }

        /* Quiz box */
        .quiz-box {
            font-size: 0.95em;
            background: black;
            color: white;
            padding: 8px 10px;
            border-radius: 8px;
            margin-top: 5px;
        }

    </style>
    """,
    unsafe_allow_html=True
)

# --- Header ---
st.markdown("<h1>🎙️ PolyVoice</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:gray;'>Accessible AI explanations with voice and trusted sources.</p>", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "widget_key" not in st.session_state:
    st.session_state["widget_key"] = 0

# --- Sidebar ---
st.sidebar.header("Personalize Learning")
level_choice = st.sidebar.selectbox(
    "1. Reading Level / Focus:",
    ["Elementary /(Dyslexia)", " ADHD", "Plain Language"]
)

level_map = {
    "1. Elementary (Dyslexia Focus)": "elementary-dyslexia",
    "2. High School (ADHD Focus)": "adhd",
    "3. Plain Language (Clarity)": "plain",
    "4. Standard Research Mode": "standard-research" # Added new mode
}
level_choice_label = st.sidebar.selectbox(
    "1. Reading Level / Focus:",
    list(level_map.keys())
)
selected_level = level_map[level_choice_label]


voice_map = {
    "Teacher-Like": "c1uwEpPUcC16tq1udqxk",
    "Calm": "z2sgjL6ER8zZEFccuQMN",
    "Energetic": "NVp9wQor3NDIWcxYoZiW"
}

voice_choice = st.sidebar.selectbox("2. Voice Style:", list(voice_map.keys()))
selected_voice_id = voice_map[voice_choice]

pace_choice = st.sidebar.select_slider(
    "3. Speech Pace:",
    options=["0.85x", "0.95x", "1.0x", "1.15x"],
    value="1.0x"
)

# --- Chat Display ---
if st.session_state["messages"]:  
    st.markdown("---")
chat_container = st.container()


with chat_container:
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-bubble'><b>🧑‍🎓 You:</b> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-bubble'><b>Assistant:</b> {msg['content']}</div>", unsafe_allow_html=True)

            # --- Source links ---
            if "references" in msg and msg["references"]:
                source_links = []
                for ref in msg["references"]:
                    try:
                        site = urllib.parse.urlparse(ref['url']).netloc.replace("www.", "")
                        if len(site) > 15:
                            site = site.split(".")[0]
                    except:
                        site = "source"
                    link_html = f"<a href='{ref['url']}' target='_blank' style='margin-right:8px; color:#0078FF; text-decoration:none;'>{site}</a>"
                    source_links.append(link_html)
                joined_links = " • ".join(source_links)
                st.markdown(f"<p style='font-size:0.9em; margin:5px 0 0 10px;'>{joined_links}</p>", unsafe_allow_html=True)

            # --- Quiz ---
            if "quiz" in msg and msg["quiz"]:
                st.markdown(f"<div class='quiz-box'><b>🧠 Quick Check:</b> {msg['quiz']}</div>", unsafe_allow_html=True)

            if "flowchart" in msg and msg["flowchart"]:
                st.subheader("📊 Lesson Flowchart")
                
                st.code(msg["flowchart"], language='mermaid') 
            # --- Voice ---
            generate_and_play(msg["content"], selected_voice_id, msg["id"], float(pace_choice.replace("x", "")))

# --- Input box ---
st.markdown("---")
with st.form(key="chat_form"):
    cols = st.columns([10, 1])
    with cols[0]:
        user_input = st.text_input(
            label="",
            placeholder="Ask a question or topic...",
            key=f"input_{st.session_state.widget_key}",
        )
    with cols[1]:
        submitted = st.form_submit_button("➤")

    if submitted and user_input.strip():
        # Define user_query here BEFORE using it
        user_query = user_input.strip()

        # Append user message
        st.session_state["messages"].append({"role": "user", "content": user_query})

        # Keep current history reference
        current_history = st.session_state["messages"]

        with st.spinner("Thinking..."):
            result = run_pipeline(
                cb,                 # Cerebras Client
                exa,                # Exa Client
                user_query,         # Query string
                selected_level,     # Complexity Level
                current_history     # Chat history
            )

        msg_id = len(st.session_state["messages"])
        st.session_state["messages"].append({
            "role": "assistant",
            "content": result["simplified_text"],
            "references": result.get("references", []),
            "quiz": result.get("quiz_text", ""),
            "flowchart": result.get("flowchart_text", ""),
            "id": msg_id
        })

        # Increment key to clear input
        st.session_state.widget_key += 1
        st.rerun()
