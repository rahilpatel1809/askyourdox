from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

class RAGEngine:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectordb = Chroma(embedding_function=self.embeddings, persist_directory="./chroma_db")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.llm = Ollama(model="mistral:latest", temperature=0.1)
        self.qa_chain = None
        self.loaded_docs = {}

    def load_doc(self, text, doc_id):
        docs = self.text_splitter.create_documents([text], metadatas=[{"doc_id": doc_id}] * len(text))
        self.vectordb.add_documents(docs)
        self.loaded_docs[doc_id] = text
        self._refresh_qa_chain()

    def remove_doc(self, doc_id):
        self.vectordb._collection.delete(where={"doc_id": doc_id})
        if doc_id in self.loaded_docs:
            del self.loaded_docs[doc_id]
        self._refresh_qa_chain()

    def _refresh_qa_chain(self):
        if self.loaded_docs:
            retriever = self.vectordb.as_retriever()
            self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm, retriever=retriever)
        else:
            self.qa_chain = None

    def ask(self, question, no_context=False):
        if no_context or not self.qa_chain:
            return self.llm.invoke(question)
        return self.qa_chain.run(question)