from langchain_community.vectorstores import Chroma
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.schema import Document


def store_embeddings(chunks, embedder, persist_dir="vectordb"):
    db = Chroma.from_documents(chunks, embedder, persist_directory=persist_dir)
    db.persist()
    return db

def load_existing_embeddings(embedder, persist_dir="vectordb"):
    return Chroma(persist_directory=persist_dir, embedding_function=embedder)