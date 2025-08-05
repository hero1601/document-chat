from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st

@st.cache_resource(show_spinner=False)
def load_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L12-v2")

def load_and_chunk(path):
    loader = PyPDFLoader(path)
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=75)
    chunks = splitter.split_documents(docs)
    return chunks

def embed_and_store(chunks):
    embeddings = load_embeddings()
    db = FAISS.from_documents(chunks, embedding=embeddings)
    return db
