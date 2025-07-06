import os
import streamlit as st
from utils import extract_text
from langchain_rag import RAGEngine
from io import BytesIO
import streamlit.components.v1 as components
import time

os.environ["GROQ_API_KEY"] = st.secrets["groq_api_key"]

st.set_page_config(page_title="AskYourDox", layout="wide")
st.title("AskYourDox 📄")

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = {}

if "doc_indexed" not in st.session_state:
    st.session_state.doc_indexed = {}

if "query" not in st.session_state:
    st.session_state.query = ""

if "answer" not in st.session_state:
    st.session_state.answer = ""

if "trigger_ask" not in st.session_state:
    st.session_state.trigger_ask = False

@st.cache_resource
def get_rag():
    return RAGEngine()

with st.spinner("Initializing AskYourDox..."):
    rag = get_rag()

files = st.file_uploader(
    "Upload Your Documents",
    type=["pdf", "docx", "txt", "jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if files:
    for file in files:
        filetype = file.type
        doc_id = file.name

        if doc_id not in st.session_state.uploaded_docs:
            file_buffer = BytesIO(file.getvalue())
            text = extract_text(file_buffer, filetype)

            st.session_state.uploaded_docs[doc_id] = text
            rag.load_doc(text, doc_id)
            st.session_state.doc_indexed[doc_id] = True
            st.success(f"{doc_id} uploaded and indexed!")

with st.form("ask_form"):
    user_query = st.text_input("#### Ask a Question:", value=st.session_state.query)
    submitted = st.form_submit_button("Ask")

if submitted:
    st.session_state.query = user_query
    st.session_state.trigger_ask = True

if st.session_state.trigger_ask:
    with st.spinner("Thinking..."):
        if st.session_state.uploaded_docs:
            st.session_state.answer = rag.ask(st.session_state.query)
        else:
            st.session_state.answer = rag.ask(st.session_state.query, no_context=True)

    st.session_state.trigger_ask = False
    st.session_state.answer_displayed = ""

if st.session_state.answer:
    st.markdown("<a name='answer'></a>", unsafe_allow_html=True)
    st.markdown("### 🧠 Answer")

    output_box = st.empty()

    if "answer_displayed" in st.session_state and st.session_state.answer_displayed == "":
        typed = ""
        for word in st.session_state.answer.split():
            typed += word + " "
            output_box.markdown(typed)
            time.sleep(0.05)
        st.session_state.answer_displayed = typed
    else:
        output_box.markdown(st.session_state.answer)

    components.html("""
        <script>
            const el = document.getElementsByName("answer")[0];
            if (el) el.scrollIntoView({ behavior: "smooth" });
        </script>
    """, height=0)