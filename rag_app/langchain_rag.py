from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

class RAGEngine:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectordb = None
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.llm = Ollama(model="mistral", temperature=0.2)
        self.qa_chain = None
        self.loaded_docs = {}

    def load_doc(self, text, doc_id):
        docs = self.text_splitter.create_documents([text], metadatas=[{"doc_id": doc_id}] * len(text))
        if self.vectordb is None:
            self.vectordb = FAISS.from_documents(docs, self.embeddings)
        else:
            self.vectordb.add_documents(docs)
        self.loaded_docs[doc_id] = text
        self._refresh_qa_chain()

    def remove_doc(self, doc_id):
        if self.vectordb:
            remaining_docs = []
            for other_id, text in self.loaded_docs.items():
                if other_id != doc_id:
                    docs = self.text_splitter.create_documents([text], metadatas=[{"doc_id": other_id}] * len(text))
                    remaining_docs.extend(docs)
            if remaining_docs:
                self.vectordb = FAISS.from_documents(remaining_docs, self.embeddings)
            else:
                self.vectordb = None
        self.loaded_docs.pop(doc_id, None)
        self._refresh_qa_chain()

    def _refresh_qa_chain(self):
        if self.vectordb and self.loaded_docs:
            retriever = self.vectordb.as_retriever()
            self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm, retriever=retriever)
        else:
            self.qa_chain = None

    def ask(self, question, no_context=False):
        if no_context or not self.qa_chain:
            return self.llm.invoke(question)
        return self.qa_chain.run(question)