# [AskYourDox](https://askyourdox.streamlit.app)

*AskYourDox* is a Streamlit web app that allows users to upload documents (PDF, DOCX, TXT, images) and ask questions based on their content. It uses a Retrieval-Augmented Generation (RAG) pipeline powered by Groq's fast inference with Llama-3.1-8b.

## Live Demo
[askyourdox.streamlit.app](https://askyourdox.streamlit.app)

## Features

- **Multi-format Uploads:** Supports PDF, DOCX, TXT, and image files using format-specific parsers.
- **OCR with EasyOCR:** For scanned images or non-digital PDFs, EasyOCR extracts readable text.
- **Vector Database:** Splits documents into chunks and stores them in a FAISS vector store through the all-MiniLM-L6-v2 embedding model.
- **Hosted LLM:** Fast response generation using Llama-3.1-8b hosted by Groq.
- **RAG-based QA:** Does Retrieval Augmented Generation via the Langchain framework on uploaded documents.

## Tech Stack

- **Streamlit:** Web interface
- **LangChain:** RAG orchestration
- **EasyOCR, PyMuPDF, python-docx:** Document parsers
- **all-MiniLM-L6-v2:** Hugging Face Sentence Transformer used for text embedding
- **FAISS:** Vector database for storing embedded document chunks
- **Groq + Llama-3.1-8b:** Language model inference

## Setup Instructions

1. Clone the repository:<br>
``
git clone https://github.com/rahilpatel1809/askyourdox.git
cd askyourdox
``<br><br>
2. Create and activate a virtual environment:<br>
``
python -m venv .venv
.venv\Scripts\activate   # On Windows
``  or <br>
``
source .venv/bin/activate   # On macOS/Linux
``<br><br>
3. Install dependencies:<br>
``
pip install -r requirements.txt
``<br><br>
4. Create a secrets file at rag_app/.streamlit/secrets.toml:<br>
``
groq_api_key = "your-groq-api-key"
``<br><br>
5. Run the app:<br>
``
cd rag_app
streamlit run app.py
``
