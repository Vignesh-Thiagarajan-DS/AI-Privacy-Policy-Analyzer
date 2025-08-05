import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import chromadb

print("Starting data ingestion...")

# Basic Setup
Settings.llm = Ollama(model="llama3", request_timeout=120.0)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

# Initialize ChromaDB
print("Initializing ChromaDB at the project root...")
db = chromadb.PersistentClient(path="../chroma_db")
chroma_collection = db.get_or_create_collection("privacy_policy_analyzer")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load Documents and Build Index
print("Loading documents from './Input Files' directory...")
reader = SimpleDirectoryReader("./Input Files")
documents = reader.load_data()
print(f"Loaded {len(documents)} document(s).")

# Create the index and store embeddings
print("Creating index and storing embeddings in ChromaDB...")
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

print("Ingestion Complete!")