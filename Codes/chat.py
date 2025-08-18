import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Legal Chat",
    page_icon="💬",
    layout="centered",
)

st.title("⚖️ AI Legal Chat")
st.caption("Paste a legal document below and ask questions about it.")

# --- Reusable Ollama Streaming Function ---
def query_ollama_stream(prompt_text, model='llama3'):
    """
    Sends a prompt to the Ollama API and yields the response in a stream.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt_text,
        "stream": True
    }
    try:
        with requests.post(url, json=payload, stream=True, timeout=300) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if chunk.get("response"):
                        yield chunk["response"]
    except requests.exceptions.RequestException as e:
        yield f"Error connecting to Ollama: {e}"

# --- Main App UI ---

# 1. Text area for the user to paste the legal document
st.subheader("1. Provide Document Context")
document_text = st.text_area("Paste the full text of your NDA or agreement here:", height=250, placeholder="Your document text goes here...")

# 2. Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Handle new chat input
if prompt := st.chat_input("Ask a question about the document..."):
    # Check if document context is provided
    if not document_text:
        st.warning("Please paste a document into the context area above before asking a question.")
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            # Construct the full prompt with the document context
            full_prompt = f"""
            **Document Context:**
            ---
            {document_text}
            ---

            **User's Question:**
            {prompt}

            **Instruction:**
            Based ONLY on the document context provided, please answer the user's question.
            """
            # Use st.write_stream to display the streaming response
            response = st.write_stream(query_ollama_stream(full_prompt))
        
        # Add the complete assistant response to the chat history
        st.session_state.messages.append({"role": "assistant", "content": response})