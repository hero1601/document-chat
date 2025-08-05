import streamlit as st
from process import load_and_chunk, embed_and_store
from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

st.set_page_config(page_title="Chat with Document")
st.title("📄 Chat with your Document")
load_dotenv()

# To handle deadlocks. Can later on turn on if high-throughput needed
os.environ["TOKENIZERS_PARALLELISM"] = "false"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None


uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:

    if st.session_state.uploaded_file_name != uploaded_file.name:
        st.session_state.uploaded_file_name = uploaded_file.name
        os.makedirs("sample_docs", exist_ok=True)
        file_path = f"sample_docs/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner("Running..."):
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
        
        st.session_state.qa_chain = qa_chain

    if st.session_state.qa_chain:
        query = st.text_input("Ask a question about the document:")
        if query:
            result = st.session_state.qa_chain.invoke({
                "question": query,
                "chat_history": st.session_state.chat_history
            })
            
            # Update and display chat history
            st.session_state.chat_history.append((query, result['answer']))

            st.markdown("### Answer")
            st.write(result['answer'])

            # Optional: Display chat history for reference
            with st.expander("🕒 Chat History"):
                for i, (q, a) in enumerate(st.session_state.chat_history):
                    st.markdown(f"**Q{i+1}:** {q}")
                    st.markdown(f"**A{i+1}:** {a}")
