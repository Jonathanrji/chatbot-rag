import streamlit as st
from ingest import ingest_document
from rag_chain import create_rag_chain
import os
import time

st.set_page_config(page_title="CHATBOT-RAG + LangSmith + Ollama", layout="centered")
st.title("CHATBOT-RAG con LangChain + Ollama + LangSmith")

# Sidebar: configuración del modelo
st.sidebar.header("⚙️ Configuración del modelo")

temperature = st.sidebar.slider("Temperatura", 0.0, 1.5, 0.8, 0.1)
top_p = st.sidebar.slider("Top-p (nucleus sampling)", 0.0, 1.0, 0.95, 0.05)
top_k = st.sidebar.slider("Top-k", 0, 100, 40, 5)
num_predict = st.sidebar.slider("Tokens generados", 64, 1024, 256, 64)

# Botón para limpiar historial
if st.sidebar.button("🗑️ Limpiar historial de conversación"):
    st.session_state.chat_history = []
    st.sidebar.success("Historial limpiado.")

# Inicializar variables de sesión
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Subida de archivo PDF
uploaded_file = st.file_uploader("📄 Sube un archivo PDF", type="pdf")
if uploaded_file is not None:
    file_path = os.path.join("data", uploaded_file.name)
    os.makedirs("data", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Verificando almacenamiento..."):
        if not os.path.exists("./chroma_db") or not os.listdir("./chroma_db"):
            ingest_document(file_path)
            st.success("✅ Documento procesado y vectorizado.")
        else:
            st.info("🗂️ Ya existe un vectorstore, usando el existente.")

        st.session_state.qa_chain = create_rag_chain(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            num_predict=num_predict
        )

# Mostrar historial completo de conversación tipo chat
if st.session_state.chat_history:
    for q, a, srcs in st.session_state.chat_history:
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(q)
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(a)
            with st.expander("📚 Fuente(s)", expanded=False):
                for doc in srcs:
                    st.markdown(f"- {doc.metadata.get('source', 'Desconocido')}")

# Campo de entrada tipo chat al final
if st.session_state.qa_chain:
    question = st.chat_input("Haz una pregunta sobre el documento...")
    if question:
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(question)

        with st.chat_message("assistant", avatar="🤖"):
            with st.status("Pensando..."):
                result = st.session_state.qa_chain.invoke(question)
                answer = result["result"]
                sources = result["source_documents"]

            # Simulación de escritura tipo streaming
            response_placeholder = st.empty()
            full_response = ""
            for word in answer.split():
                full_response += word + " "
                response_placeholder.markdown(full_response + "▌")
                time.sleep(0.03)
            response_placeholder.markdown(full_response)

            with st.expander("📚 Fuente(s)", expanded=False):
                for doc in sources:
                    st.markdown(f"- {doc.metadata.get('source', 'Desconocido')}")

            # Guardar en historial
            st.session_state.chat_history.append((question, answer, sources))
