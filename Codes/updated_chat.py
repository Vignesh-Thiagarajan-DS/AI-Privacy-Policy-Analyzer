import streamlit as st
import os
import requests
import json
import fitz  # PyMuPDF
import time

# --- App Configuration ---
st.set_page_config(
    page_title="Aegis - Legal Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Safe Custom CSS ---
st.markdown("""
<style>
    /* Hide the default sidebar arrow for a cleaner look */
    [data-testid="stSidebarCollapseIcon"] { visibility: hidden; }
    
    /* PRO Badge Styling */
    .pro-badge {
        background-color: #7F56D9; color: white; padding: 2px 8px;
        border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 8px;
    }
    
    /* Rounded, neat sidebar buttons */
    div[data-testid="stSidebar"] button {
        border-radius: 10px !important;
    }

    /* Welcome screen centering */
    .welcome-container { text-align: center; margin-top: 15vh; }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def query_ollama_stream(prompt_text, model='llama3'):
    """Streams the response from the local Ollama instance."""
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt_text, "stream": True}
    try:
        with requests.post(url, json=payload, stream=True, timeout=600) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if chunk.get("response"):
                        yield chunk["response"]
    except requests.exceptions.RequestException as e:
        yield f"Connection Error: Please ensure 'ollama serve' is running. ({e})"

def parse_file(uploaded_file):
    """Extracts text from PDF or TXT files."""
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
    first_id = f"chat_{int(time.time())}"
    st.session_state.current_session_id = first_id
    st.session_state.sessions[first_id] = {"messages": [], "context": {}, "name": "New Chat"}

current_session = st.session_state.sessions[st.session_state.current_session_id]

# --- Sidebar: History & Rock-Solid Uploader ---
with st.sidebar:
    st.title("☰ Chat History")
    
    # New Chat Button
    if st.button(" :material/edit_note: New Chat", use_container_width=True):
        new_id = f"chat_{int(time.time())}"
        st.session_state.sessions[new_id] = {"messages": [], "context": {}, "name": "New Chat"}
        st.session_state.current_session_id = new_id
        st.rerun()

    # Chat History List
    st.write("---")
    for s_id, s_data in st.session_state.sessions.items():
        if st.button(f"📄 {s_data['name'][:20]}", key=s_id, use_container_width=True):
            st.session_state.current_session_id = s_id
            st.rerun()

    st.write("---")
    st.subheader("1. Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF/TXT files", 
        type=['pdf', 'txt'], 
        accept_multiple_files=True,
        help="Upload files here before asking questions."
    )
    
    if uploaded_files:
        for f in uploaded_files:
            if f.name not in current_session["context"]:
                with st.spinner(f"Reading {f.name}..."):
                    current_session["context"][f.name] = parse_file(f)
                st.toast(f"{f.name} added!")

    st.subheader("2. Active Context")
    if not current_session["context"]:
        st.caption("No files attached.")
    else:
        for i, doc_name in enumerate(current_session["context"].keys(), 1):
            st.markdown(f"**{i}.** `{doc_name}`")
            
    if st.button("🗑️ Clear Files", use_container_width=True):
        current_session["context"] = {}
        st.rerun()

# --- Main UI Header ---
st.header("Aegis Legal Assistant")
st.caption("Running securely on your local LLM.")


# --- Chat Display ---
if not current_session["messages"]:
    # Welcome Screen
    st.markdown('<div class="welcome-container"><h1 style="font-weight: 700;">Welcome!</h1><p style="color: grey;">Start a conversation or upload documents in the sidebar to begin analysis.</p></div>', unsafe_allow_html=True)
else:
    # Message History
    for msg in current_session["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- Native, Uninterrupted Chat Input ---
if prompt := st.chat_input("Message Aegis..."):
    
    # Dynamic Chat Renaming (Updates sidebar title silently)
    if current_session["name"] == "New Chat":
        words = prompt.split()
        current_session["name"] = " ".join(words[:5]) + ("..." if len(words) > 5 else "")
    
    # 1. Save and display user message immediately
    current_session["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate assistant response
    with st.chat_message("assistant"):
        # Compile all uploaded documents into the prompt
        compiled_context = ""
        if current_session["context"]:
            compiled_context = "The following documents are provided for context:\n\n"
            for name, text in current_session["context"].items():
                compiled_context += f"--- START OF {name} ---\n{text}\n--- END OF {name} ---\n\n"
        else:
            compiled_context = "No context documents provided. Answer generally."

        final_prompt = f"{compiled_context}\n\nUser Question: {prompt}\n\nInstruction: Answer the user's question based strictly on the provided context documents if they exist."
        
        # 3. Show spinner while Ollama evaluates the context
        with st.spinner("Aegis is analyzing documents..."):
            stream = query_ollama_stream(final_prompt)
        
        # 4. Stream the output reliably
        response = st.write_stream(stream)
        
        # 5. Save to history
        current_session["messages"].append({"role": "assistant", "content": response})