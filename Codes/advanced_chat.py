import streamlit as st
import requests
import json
import fitz  # PyMuPDF
import time
import os
import base64

# --- App Configuration ---
st.set_page_config(
    page_title="Aegis", # Changed the project name as requested
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Helper Functions ---
def image_to_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# --- Custom CSS for UI Polish ---
st.markdown("""
<style>
    /* General body styling */
    .stApp {
        background-color: #0E1117; /* Streamlit's default dark theme background */
    }
    /* PRO Badge styling */
    .pro-badge {
        background-color: #7F56D9;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-left: 8px;
        vertical-align: middle;
    }
    /* Custom styling for chat history buttons in sidebar */
    div[data-testid="stSidebar"] button {
        width: 100%;
        text-align: left;
        padding: 8px;
        border-radius: 8px;
        background-color: transparent;
        border: none;
    }
    div[data-testid="stSidebar"] button:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    /* Hide Streamlit footer */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# (All your other helper functions like query_ollama_stream and parse_file remain the same)
def query_ollama_stream(prompt_text, model='llama3'):
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt_text, "stream": True}
    try:
        with requests.post(url, json=payload, stream=True, timeout=300) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if chunk.get("response"):
                        yield chunk["response"]
    except requests.exceptions.RequestException as e:
        yield f"Error: Could not connect to Ollama. {e}"

def parse_file(uploaded_file):
    if uploaded_file.type == "text/plain":
        return uploaded_file.getvalue().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        with fitz.open(stream=uploaded_file.getvalue(), filetype="pdf") as doc:
            return "".join(page.get_text() for page in doc)
    return None

# --- Session State Initialization ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {}

if "current_session_id" not in st.session_state:
    first_session_id = f"chat_{int(time.time())}"
    st.session_state.current_session_id = first_session_id
    st.session_state.sessions[first_session_id] = {
        "messages": [], "document_context": None, "document_name": "New Chat"
    }

def get_current_session():
    return st.session_state.sessions[st.session_state.current_session_id]

# --- Sidebar for Chat Management ---
with st.sidebar:
    st.title("Aegis v0.1") # Using the new project name
    if st.button("➕ New Chat", use_container_width=True):
        new_session_id = f"chat_{int(time.time())}"
        st.session_state.sessions[new_session_id] = {
            "messages": [], "document_context": None, "document_name": "New Chat"
        }
        st.session_state.current_session_id = new_session_id
        st.rerun()

    st.write("---")
    sorted_sessions = sorted(st.session_state.sessions.items(), key=lambda item: int(item[0].split('_')[1]), reverse=True)
    for session_id, session_data in sorted_sessions:
        chat_title = session_data.get("document_name", "New Chat")
        if st.button(f"📄 {chat_title[:30]}", key=session_id, help=chat_title):
            st.session_state.current_session_id = session_id
            st.rerun()

# --- Main Chat Interface ---

# NEW/IMPROVED: A single header row for better alignment
col1, col2 = st.columns([5, 1])
with col1:
    # Use a placeholder to create space, title is now part of the welcome message
    st.header("Aegis! 🛡️ - Legal Assistant (Running on Local LLM)") 
with col2:
    image_path = "Static/Vignesh_DP.jpg"
    try:
        image_b64 = image_to_base64(image_path)
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: flex-end;">
                <img src="data:image/jpeg;base64,{image_b64}" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;">
                <div style="line-height: 1;">
                    <span style="font-weight: bold;">Vignesh</span>
                    <span class="pro-badge">PRO</span>
                </div>
            </div>
            """, unsafe_allow_html=True
        )
    except FileNotFoundError:
        # Fallback if image not found
        st.markdown('<p style="text-align: right; font-weight: bold;">Vignesh <span class="pro-badge">PRO</span></p>', unsafe_allow_html=True)

st.write("---")

current_session = get_current_session()

# Display chat messages for the current session
for message in current_session["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# NEW/IMPROVED: Handle the initial "empty" state with custom, larger text
if not current_session["document_context"]:
    # Using st.markdown for custom styling
    st.markdown(
        """
        <div style="text-align: center; margin-top: 50px;">
            <h2 style="font-weight: 500;">Welcome, Vignesh!</h2>
            <p style="color: #888;">Start a new analysis by uploading a document.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    uploaded_file = st.file_uploader(
        "Drag and drop a TXT or PDF file here",
        type=['txt', 'pdf'],
        key=f"uploader_{st.session_state.current_session_id}"
    )
    
    if uploaded_file:
        with st.spinner("Analyzing your document... ⏳"):
            context = parse_file(uploaded_file)
            current_session["document_context"] = context
            file_name_without_ext = os.path.splitext(uploaded_file.name)[0]
            current_session["document_name"] = file_name_without_ext
            current_session["messages"].append({
                "role": "assistant",
                "content": f"I've finished analyzing `{uploaded_file.name}`. What would you like to know?"
            })
        st.success("Document analysis complete!")
        time.sleep(1)
        st.rerun()

# Chat input is shown only after a document is uploaded
if current_session["document_context"]:
    if prompt := st.chat_input("Ask a question about the document..."):
        current_session["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            full_prompt = f"""
            **Document Context:**\n---\n{current_session['document_context']}\n---\n
            **User's Question:** {prompt}\n
            **Instruction:** Based ONLY on the document context provided, answer the user's question.
            """
            response_stream = query_ollama_stream(full_prompt)
            full_response = st.write_stream(response_stream)
        
        current_session["messages"].append({"role": "assistant", "content": full_response})