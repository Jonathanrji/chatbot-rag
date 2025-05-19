import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langsmith import traceable
from langchain.callbacks import LangChainTracer

@traceable(name="rag_chain_with_langsmith")
def create_rag_chain(model="llama3:latest", temperature=0.8, top_p=0.95, top_k=40, num_predict=256):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")   # Embeddings con nomic-embed-text
    
    # Vector store persistente
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    retriever = vectorstore.as_retriever()

    # LLM para generación con parámetros configurables
    llm = ChatOllama(
        model=model,
        base_url="http://localhost:11434",
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        num_predict=num_predict
    )


    # LangSmith tracing
    tracer = LangChainTracer()
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        callbacks=[tracer]
    )
    
    return qa_chain
