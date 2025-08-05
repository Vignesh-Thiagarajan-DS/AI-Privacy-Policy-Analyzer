import streamlit as st
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import chromadb
import os

# Page Configuration
st.set_page_config(
    page_title="AI Privacy Policy Analyzer",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("AI Privacy Policy Analyzer")
st.caption("Analyze legal documents against internal guidelines using Llama 3.")

# System Initialization (with caching for performance)
@st.cache_resource
def initialize_system():
    """
    Initializes the AI model, embedding model, and vector database connection.
    Uses Streamlit's caching to load these components only once.
    """
    st.write("Initializing system... (This happens only once)")
    # Setup LLM and embedding model
    Settings.llm = Ollama(model="llama3", request_timeout=300.0)
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

    # Connect to the existing ChromaDB collection
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("privacy_policy_analyzer")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # Load the index from the vector store
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    
    # Return a query engine with a higher similarity top_k for more context
    return index.as_query_engine(similarity_top_k=3)

try:
    query_engine = initialize_system()
except Exception as e:
    st.error(f"Failed to initialize the system: {e}")
    st.stop()

# UI: Document Selection
st.subheader("1. Select a Document to Analyze")

# Define document options based on files in the "Input Files" directory
doc_folder = "./Input Files"
# We exclude the policy guidelines from the dropdown list
doc_options = [f for f in os.listdir(doc_folder) if f != "policy_guidelines.txt"]

selected_doc_filename = st.selectbox(
    "Choose a document:",
    options=doc_options,
    index=0 # Default to the first document in the list
)

# Display the content of the selected document in an expander
if selected_doc_filename:
    with open(os.path.join(doc_folder, selected_doc_filename), "r") as f:
        doc_content = f.read()
    with st.expander("View Selected Document Content"):
        st.text_area("Content", doc_content, height=250)

# UI: Analysis Trigger
st.subheader("2. Run Analysis")

# This is the detailed prompt that instructs the LLM on how to behave.
# It's the core of the "professional" output.
analysis_prompt = (
    f"You are a meticulous legal compliance analyst. Your task is to analyze the provided document, '{selected_doc_filename}', "
    f"strictly against our company's 'policy_guidelines.txt'.\n\n"
    f"For each of the 4 guidelines in our policy, perform the following steps:\n"
    f"1. **Guideline Reference:** State the guideline you are analyzing (e.g., 'Confidentiality Term').\n"
    f"2. **Clause Identification:** Quote the specific clause or text from '{selected_doc_filename}' that is relevant to the guideline. If no relevant clause is found, state that explicitly.\n"
    f"3. **Risk Assessment:** Assign a clear risk level: **Low Risk**, **Medium Risk**, **High Risk**, or **Unacceptable**. \n"
    f"4. **Justification:** Provide a concise, one-sentence justification explaining your risk assessment based on how the document's clause aligns with our policy guideline.\n\n"
    f"Present your final analysis in a clear, structured format."
)

if st.button("Analyze Document", type="primary"):
    if not selected_doc_filename:
        st.warning("Please select a document first.")
    else:
        with st.spinner("AI is analyzing the document... This may take a moment."):
            try:
                response = query_engine.query(analysis_prompt)
                st.subheader("Analysis Results")
                st.info(str(response))
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")