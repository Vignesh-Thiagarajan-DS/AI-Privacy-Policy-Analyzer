import streamlit as st
import os
import requests
import json
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
import chromadb

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Privacy Policy Analyzer",
    page_icon="⚖️",
    layout="centered",
)

st.title("⚖️ AI Privacy Policy Analyzer")
st.caption("Analyze legal documents against internal guidelines using Llama 3.")

# --- System Initialization ---
@st.cache_resource
def initialize_retriever():
    st.write("Initializing system... (This happens only once)")
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("privacy_policy_analyzer")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    return index.as_retriever(similarity_top_k=4)

# MODIFIED function to handle streaming
def query_ollama_stream(prompt_text):
    """
    Sends a prompt to the Ollama API and yields the response in a stream.
    This is now a generator function.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3",
        "prompt": prompt_text,
        "stream": True # This is the crucial change to enable streaming
    }
    try:
        # The requests call now also uses stream=True
        with requests.post(url, json=payload, stream=True, timeout=300) as response:
            response.raise_for_status()
            # We iterate over the response line by line
            for line in response.iter_lines():
                if line:
                    # Each line is a JSON object; we parse it and yield the content
                    chunk = json.loads(line)
                    if chunk.get("response"):
                        yield chunk["response"]
    except requests.exceptions.RequestException as e:
        yield f"Error connecting to Ollama: {e}"

try:
    retriever = initialize_retriever()
except Exception as e:
    st.error(f"Failed to initialize the retriever: {e}", icon="🔥")
    st.stop()

# --- UI ---
st.subheader("1. Select a Document to Analyze")
doc_folder = "./Input Files"
doc_options = [f for f in os.listdir(doc_folder) if f != "policy_guidelines.txt"]
selected_doc_filename = st.selectbox("Choose a document:", options=doc_options, index=0)

if selected_doc_filename:
    with open(os.path.join(doc_folder, selected_doc_filename), "r") as f:
        doc_content = f.read()
    with st.expander("View Selected Document Content"):
        st.text_area("Content", doc_content, height=250)

st.subheader("2. Run Analysis")
analysis_prompt_template = (
    "You are a meticulous legal compliance analyst. Your task is to analyze the provided document "
    "strictly against our company's policy guidelines, which are included below.\n\n"
    "--- POLICY GUIDELINES & DOCUMENT CONTEXT ---\n"
    "{context_str}\n"
    "--- END OF CONTEXT ---\n\n"
    "Based on the context above, analyze the document '{doc_name}'. "
    "For each policy guideline, perform the following steps:\n"
    "1. **Guideline Reference:** State the guideline you are analyzing (e.g., 'Confidentiality Term').\n"
    "2. **Clause Identification:** Quote the specific clause or text from the document. If no clause is found, state that explicitly.\n"
    "3.  **Risk Assessment:** Assign a clear risk level: **Low Risk**, **Medium Risk**, **High Risk**, or **Unacceptable**.\n"
    "4. **Justification:** Provide a concise, one-sentence justification for your risk assessment.\n"
)

if st.button("Analyze Document", type="primary"):
    with st.spinner("Retrieving context and starting analysis..."):
        retrieved_nodes = retriever.retrieve(f"Analysis of document {selected_doc_filename}")
        context_str = "\n\n".join([n.get_content() for n in retrieved_nodes])
        final_prompt = analysis_prompt_template.format(
            context_str=context_str, 
            doc_name=selected_doc_filename
        )

    st.subheader("Analysis Results")
    # MODIFIED way to display the response
    # st.write_stream consumes the generator and displays the output in real-time.
    st.write_stream(query_ollama_stream(final_prompt))