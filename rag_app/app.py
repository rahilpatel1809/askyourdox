import streamlit as st
from utils import extract_text
from langchain_rag import RAGEngine
from io import BytesIO
import streamlit.components.v1 as components
import time

st.set_page_config(page_title="AskYourDox", layout="wide")
st.title("AskYourDox📄")

rag = RAGEngine()

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = {}

files = st.file_uploader(
    "Upload PDF, DOCX, TXT, or Image",
    type=["pdf", "docx", "txt", "jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if files:
    for file in files:
        filetype = file.type
        doc_id = file.name
        file_buffer = BytesIO(file.getvalue())
        text = extract_text(file_buffer, filetype)

        st.session_state.uploaded_docs[doc_id] = text
        rag.load_doc(text, doc_id)
        st.success(f"{doc_id} uploaded and indexed!")

if st.session_state.uploaded_docs:
    for doc_id in list(st.session_state.uploaded_docs.keys()):
        if f"remove_{doc_id}" in st.session_state:
            del st.session_state.uploaded_docs[doc_id]
            rag.remove_doc(doc_id)
            st.experimental_rerun()

query = st.text_input("#### Ask a question:")

if query:
    st.markdown("<a name='answer'></a>", unsafe_allow_html=True)
    st.markdown("### 🧠 Answer")
    with st.spinner("Thinking..."):
        if st.session_state.uploaded_docs:
            answer = rag.ask(query)
        else:
            answer = rag.ask(query, no_context=True)

    output_box = st.empty()
    typed = ""
    for word in answer.split():
        typed += word + " "
        output_box.markdown(typed)
        time.sleep(0.05)

    components.html("""
        <script>
            const el = document.getElementsByName("answer")[0];
            if (el) el.scrollIntoView({ behavior: "smooth" });
        </script>
    """, height=0)