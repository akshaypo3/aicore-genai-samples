import streamlit as st
import os
import base64
import time
from dotenv import load_dotenv
from PIL import Image
from gen_ai_hub.proxy.native.google_vertexai.clients import GenerativeModel
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from streamlit_mic_recorder import mic_recorder

# ---------- Page Config ----------
st.set_page_config(
    page_title="🧠⚡ Multimodal Intelligent Response Assistant",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': 'https://www.example.com',
        'Report a bug': None,
        'About': "### 🤖 Powered by AI\nA multimodal chatbot for intelligent interaction using audio, image, video, and text."
    }
)

# ---------- Environment Setup ----------
load_dotenv()
AICORE_AUTH_URL = os.getenv('AICORE_AUTH_URL')
AICORE_CLIENT_ID = os.getenv('AICORE_CLIENT_ID')
AICORE_CLIENT_SECRET = os.getenv('AICORE_CLIENT_SECRET')
AICORE_BASE_URL = os.getenv('AICORE_BASE_URL')
AICORE_RESOURCE_GROUP = os.getenv('AICORE_RESOURCE_GROUP')

# ---------- Load Model ----------
@st.cache_resource
def load_model():
    proxy_client = get_proxy_client("gen-ai-hub")
    return GenerativeModel(
        deployment_id="Enter Your Model Deployement ID",
        model_name="gemini-2.0-flash",
        proxy_client=proxy_client
    )

model = load_model()

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "file_type" not in st.session_state:
    st.session_state.file_type = None
if "file_bytes" not in st.session_state:
    st.session_state.file_bytes = None
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0

# ---------- Response Generator ----------
def generate_response(input_text=None):
    user_parts = []

    if input_text:
        user_parts.append({"text": input_text})

    # Attach file only in the first user message
    if st.session_state.file_bytes and not any(
        m["role"] == "user" and any("text" in p for p in m.get("parts", []))
        for m in st.session_state.messages
    ):
        encoded_file = base64.b64encode(st.session_state.file_bytes).decode('utf-8')

        if st.session_state.file_type == "audio":
            mime_type = "audio/wav"
            user_parts.insert(0, {
                "inline_data": {"mime_type": mime_type, "data": encoded_file}
            })
        elif st.session_state.file_type == "image":
            mime_type = Image.open(st.session_state.uploaded_file).get_format_mimetype()
            user_parts.insert(0, {
                "inline_data": {"mime_type": mime_type, "data": encoded_file}
            })
        elif st.session_state.file_type == "video":
            mime_type = "video/mp4"
            user_parts.insert(0, {
                "inline_data": {"mime_type": mime_type, "data": encoded_file}
            })

        # Clear file info after attaching
        st.session_state.file_bytes = None
        st.session_state.file_type = None
        st.session_state.uploaded_file = None

    if user_parts:
        st.session_state.messages.append({"role": "user", "parts": user_parts})

    if not st.session_state.messages:
        st.warning("Please enter text or upload a file before generating a response.")
        return ""

    response = model.generate_content(st.session_state.messages)
    st.session_state.messages.append({"role": "model", "parts": [{"text": response.text}]})
    return response.text

# ---------- Custom CSS ----------
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with open("styles.css", "w") as f:
    f.write(""" 
    .upload-section {
        border: 2px dashed #0f62fe;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f4f4f4;
        margin-bottom: 1rem;
    }
    .upload-section:hover {
        background-color: #e8e8e8;
    }
    .upload-icon {
        font-size: 3rem;
        color: #0f62fe;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #0f62fe;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0353e9;
        color: white;
    }
    .chat-header {
        color: #0f62fe;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .chat-subheader {
        color: #525252;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    """)

local_css("styles.css")

# ---------- Header ----------
logo_col, text_col = st.columns([0.1, 0.9])
with logo_col:
    st.image("sap_logo.png", width=70)
with text_col:
    st.markdown('<p class="chat-header">🧠⚡ Multimodal Intelligent Response Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="chat-subheader">🎤🖼️🎞️💬 Interact using <strong>voice</strong>, <strong>image</strong>, <strong>video</strong>, or <strong>text</strong> to receive intelligent responses.</p>', unsafe_allow_html=True)

# ---------- Upload Media ----------
with st.expander("📁 Upload Media", expanded=True):
    st.markdown("""
    <div class="custom-dropzone">
        <div class="upload-icon">⬆️</div>
        <h3>Drag and drop files into the box below 👇</h3>
        <p>Supports images, audio, and videos (PNG, JPG, MP3, WAV, MP4, MOV)</p>
    </div>
    <style>
        .custom-dropzone {
            position: relative;
            border: 2px dashed #0f62fe;
            border-radius: 10px;
            padding: 3rem 1rem;
            text-align: center;
            background-color: #f4f4f4;
            margin-bottom: 1rem;
        }
        .custom-dropzone:hover {
            background-color: #e8e8e8;
        }
        .upload-icon {
            font-size: 3rem;
            color: #0f62fe;
            margin-bottom: 1rem;
        }
        /* Hide file input but keep it clickable */
        .uploaded-file-container > div {
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            opacity: 0;
            cursor: pointer;
        }
    </style>
    """, unsafe_allow_html=True)

    # This positions the file uploader inside the styled box
    with st.container():
        st.markdown('<div class="uploaded-file-container">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            label="Upload here",
            type=["mp3", "wav", "png", "jpg", "jpeg", "mp4", "mov", "avi"],
            key=f"file_uploader_{st.session_state.file_uploader_key}",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        ext = uploaded_file.name.split('.')[-1].lower()
        st.session_state.file_bytes = uploaded_file.read()

        if ext in ["mp3", "wav"]:
            st.session_state.file_type = "audio"
            st.audio(st.session_state.file_bytes, format=f"audio/{ext}")
            st.success("🎧 Audio file ready for analysis")
        elif ext in ["png", "jpg", "jpeg"]:
            st.session_state.file_type = "image"
            st.image(st.session_state.file_bytes, use_column_width=True)
            st.success("🖼️ Image ready for analysis")
        elif ext in ["mp4", "mov", "avi"]:
            st.session_state.file_type = "video"
            st.video(st.session_state.file_bytes)
            st.success("🎞️ Video ready for analysis")


# ---------- Chat Display ----------
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "assistant"
        with st.chat_message(role):
            for part in msg["parts"]:
                if "text" in part:
                    st.markdown(part["text"])

# ---------- Text & Mic Input ----------
input_col, mic_col = st.columns([0.85, 0.15])
with input_col:
    user_input = st.chat_input("Ask anything using text...")

with mic_col:
    audio_data = mic_recorder(
        start_prompt="🎙️ Record",
        stop_prompt="⏹️ Stop",
        key="mic_recorder",
        just_once=True
    )

# ---------- Handle Text Input ----------
if user_input:
    with chat_container:
        with st.chat_message("user"):
            st.markdown(user_input)

    with st.spinner("Analyzing..."):
        response = generate_response(input_text=user_input)
        with chat_container:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for chunk in response.split(" "):
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)

# ---------- Handle Mic Input ----------
if audio_data and audio_data['bytes']:
    st.session_state.file_bytes = audio_data['bytes']
    st.session_state.file_type = "audio"

    st.session_state.messages.append({
        "role": "user",
        "parts": [
            {"inline_data": {"mime_type": "audio/wav", "data": base64.b64encode(audio_data['bytes']).decode()}},
            {"text": "Please listen to this voice and respond as if in a friendly conversation. Do not describe or transcribe it, just reply naturally."}
        ]
    })

    with chat_container:
        with st.chat_message("user"):
            st.audio(audio_data['bytes'], format="audio/wav")
            st.markdown("🎤 Voice input received")

    with st.spinner("Generating response from audio..."):
        response = model.generate_content(st.session_state.messages)
        st.session_state.messages.append({"role": "model", "parts": [{"text": response.text}]})

        with chat_container:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for chunk in response.text.split(" "):
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)

# ---------- Clear Button ----------
if st.button("🔄 Clear Conversation", type="primary"):
    st.session_state.messages = []
    st.session_state.uploaded_file = None
    st.session_state.file_type = None
    st.session_state.file_bytes = None
    st.session_state.file_uploader_key += 1
    st.rerun()
