import os
from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq
from process import load_and_chunk, embed_and_store
import streamlit as st


def process_pdf(uploaded_file):

    os.makedirs("sample_docs", exist_ok=True)
    file_path = f"sample_docs/{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    chunks = load_and_chunk(file_path)
    db = embed_and_store(chunks)

    llm = ChatGroq(
        temperature=0.2,
        model="llama3-70b-8192"
    )

    retriever = db.as_retriever()
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain


def handle_query(chat_session: dict, query: str):
    
    if not chat_session.get("qa_chain"):
        st.warning("Please upload a document first.")
        return
    
    try:
        result = chat_session["qa_chain"].invoke({
            "question": query,
            "chat_history": chat_session["history"]
        })

    except Exception as ex:
        st.error(f"Currently the server is down. Can you try little later")
        return
    
    chat_session["history"].append((query, result['answer']))

    st.markdown("### Answer")
    st.write(result['answer'])

    with st.expander("🕒 Chat History"):
        for i, (q, a) in enumerate(chat_session["history"]):
            st.markdown(f"**Q{i+1}:** {q}")
            st.markdown(f"**A{i+1}:** {a}")

