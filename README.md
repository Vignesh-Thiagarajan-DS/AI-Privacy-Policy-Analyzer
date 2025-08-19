# ⚖️ AI Legal Document Analyzer

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit)](https://streamlit.io/) [![LlamaIndex](https://img.shields.io/badge/LlamaIndex-0.10-6B45BC?logo=llama)](https://www.llamaindex.ai/) [![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-232F3E?logo=ollama)](https://ollama.com/)

A sophisticated RAG (Retrieval-Augmented Generation) system built to analyze legal documents like NDAs and B2B agreements for compliance risks. This tool leverages local LLMs to compare contract clauses against internal policies, providing real-time, streaming analysis to accelerate legal review cycles.

<br>

![Aegis App Demo](./Static/Vignesh-AI-Legal-Assistant-v01-demo.gif)

## The Problem

In any business setting, legal teams spend countless hours manually reviewing contracts. This process is:
* **Time-Consuming:** Manually reading dense legal text is slow.
* **Costly:** Legal hours are expensive.
* **Prone to Error:** Human oversight can lead to missed risks and non-compliant clauses.

This project tackles these challenges by automating the initial, repetitive stages of compliance review.

## Features

* **AI-Powered Clause Analysis:** Utilizes local, open-source LLMs (Llama 3 / Phi3) to understand and interpret complex legal language.
* **Retrieval-Augmented Generation (RAG):** The core of the system. It enriches the LLM's knowledge with custom internal policy documents, ensuring analysis is based on specific organizational rules, not just general knowledge.
* **Dynamic Risk Assessment:** Automatically flags clauses and assigns risk levels (Low, Medium, High) with justifications.
* **Interactive Frontend:** A clean, user-friendly interface built with Streamlit for easy document selection and analysis.
* **Real-Time Streaming:** The analysis report is streamed word-by-word, providing an interactive and responsive user experience.

## Tech Stack & Architecture

This project was built with a modern, open-source stack designed for building local-first LLM applications.

| Component | Technology | Description |
| :--- | :--- | :--- |
| **LLM Server** | **Ollama** | Serves open-source models like Llama 3 locally. |
| **RAG Framework** | **LlamaIndex** | Orchestrates the data pipeline from ingestion to retrieval and querying. |
| **Vector Database** | **ChromaDB** | Stores document embeddings for efficient similarity search. |
| **Web UI** | **Streamlit** | Creates the interactive user interface with Python. |
| **Language** | **Python** | The core programming language for the entire application. |

### System Architecture

The application follows a standard RAG pipeline:

```mermaid
---
config:
  layout: fixed
  look: neo
---
flowchart LR
 subgraph subGraph0["Data Ingestion & Preparation (Offline)"]
        E["Vector Database (ChromaDB)"]
        D["LlamaIndex: Embedding Generation"]
        C["LlamaIndex: Text Chunking & Splitting"]
        B["LlamaIndex: Data Loading & Parsing"]
        A["Source Documents (Legal & Policy)"]
  end
 subgraph subGraph1["Real-Time Analysis & Reporting (Online)"]
        G{"LlamaIndex: Query Engine"}
        F["User Query via UI"]
        H["Ollama LLM"]
        I["Streamlit UI: Report"]
  end
    A --> B
    B --> C
    C --> D
    D --> E
    F --> G
    G --> E
    E -- Retrieves Relevant Context --> G
    G -- Generates Contextualized Prompt --> H
    H -- Streams Analytical Insights --> I
    style A fill:#f5f5f5,color:#333,stroke:#333,stroke-width:1px
    style B fill:#e0f7fa,color:#333,stroke:#333,stroke-width:1px
    style C fill:#e0f7fa,color:#333,stroke:#333,stroke-width:1px
    style D fill:#e0f7fa,color:#333,stroke:#333,stroke-width:1px
    style E fill:#dcedc8,color:#333,stroke:#333,stroke-width:2px
    style F fill:#f5f5f5,color:#333,stroke:#333,stroke-width:1px
    style G fill:#e0f7fa,color:#333,stroke:#333,stroke-width:1px
    style H fill:#dcedc8,color:#333,stroke:#333,stroke-width:2px
    style I fill:#aed581,color:#333,stroke:#333,stroke-width:2px

```

### Local Setup & Installation
Follow these steps to run the project on your local machine.

Prerequisites
1. Python 3.10+
2. Ollama installed and running on your machine.

#### Step-by-Step Guide
1. Clone the Repository
Bash
    ```
    git clone [https://github.com/Vignesh-Thiagarajan-DS/AI-Privacy-Policy-Analyzer.git](https://github.com/Vignesh-Thiagarajan-DS/AI-Privacy-Policy-Analyzer.git)
    cd AI-Privacy-Policy-Analyzer
    ```
    
2. Create and Activate Virtual Environment
Bash
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```
    
3. Install Dependencies
Bash
    ```
    pip install -r requirements.txt
    ```
    
4. Download a Local LLM via Ollama
Bash
    ```
    ollama pull phi3:mini
    ollama pull nomic-embed-text
    ```
    
5. Ingest Your Data
Bash
    ```
    python Codes/ingest.py
    ```
    
6. Run the Streamlit Application
Bash
    ```
    streamlit run Codes/app.py
    ```

#### Usage
1. Once the app is running, select a document from the dropdown menu.
2. Click the "Analyze Document" button.
3. Watch as the analysis is streamed to the results section in real-time.

#### License
---
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
