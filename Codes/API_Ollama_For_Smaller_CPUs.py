import streamlit as st
import os
import requests # Import the new library
import json
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
import chromadb

# Page Configuration
st.set_page_config(
    page_title="AI Privacy Policy Analyzer",
    page_icon="⚖️",
    layout="centered",
)

st.title("⚖️ AI Privacy Policy Analyzer")
st.caption("Analyze legal documents against internal guidelines using Llama 3.")

# System Initialization 
@st.cache_resource
def initialize_retriever():
    """
    Initializes the embedding model and vector database to retrieve context.
    """
    st.write("Initializing system... (This happens only once)")
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("privacy_policy_analyzer")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    return index.as_retriever(similarity_top_k=4)

#function to call local Ollama API 
def query_ollama_api(prompt_text):
    """
    Sends a prompt to the Ollama API directly and returns the response.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3",
        "prompt": prompt_text,
        "stream": True # False if we are capturing the full response at once
    }
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()  
        # The response from Ollama is a stream of JSON objects, we parse the final one
        return json.loads(response.text).get("response", "Error: No response field in JSON")
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {e}"

try:
    retriever = initialize_retriever()
except Exception as e:
    st.error(f"🚨 Failed to initialize the retriever: {e}", icon="🔥")
    st.stop()

# UI: Document Selection 
st.subheader("1. Select a Document to Analyze")
doc_folder = "./Input Files"
doc_options = [f for f in os.listdir(doc_folder) if f != "policy_guidelines.txt"]
selected_doc_filename = st.selectbox("Choose a document:", options=doc_options, index=0)

if selected_doc_filename:
    with open(os.path.join(doc_folder, selected_doc_filename), "r") as f:
        doc_content = f.read()
    with st.expander("View Selected Document Content"):
        st.text_area("Content", doc_content, height=250)

# UI: Analysis Trigger
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
    "3. **Risk Assessment:** Assign a clear risk level: **Low Risk**, **Medium Risk**, **High Risk**, or **Unacceptable**.\n"
    "4. **Justification:** Provide a concise, one-sentence justification for your risk assessment.\n"
)

if st.button("Analyze Document", type="primary"):
    with st.spinner("Retrieving context and running analysis..."):
        try:
            # 1. Retrieve context from ChromaDB
            retrieved_nodes = retriever.retrieve(f"Analysis of document {selected_doc_filename}")
            context_str = "\n\n".join([n.get_content() for n in retrieved_nodes])
            
            # 2. Construct the final prompt
            final_prompt = analysis_prompt_template.format(
                context_str=context_str, 
                doc_name=selected_doc_filename
            )

            # 3. Call the Ollama API with our new function
            response = query_ollama_api(final_prompt)
            
            st.subheader("Analysis Results")
            st.info(response)
        except Exception as e:
            st.error(f"An error occurred during analysis: {e}", icon="🔥")