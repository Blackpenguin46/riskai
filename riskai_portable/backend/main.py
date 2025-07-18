### main.py
from rag_pipeline.loader import load_documents, chunk_documents
from rag_pipeline.embedder import get_embedder
from rag_pipeline.store import store_embeddings
from rag_pipeline.retriever import build_rag_chain

def main():
    print("Loading and processing documents...")
    docs = load_documents("data/")
    chunks = chunk_documents(docs)

    print("Embedding documents...")
    embedder = get_embedder()
    db = store_embeddings(chunks, embedder)

    print("Building RAG pipeline...")
    qa_chain = build_rag_chain(db)

    while True:
        query = input("\nAsk a risk-related question (or type 'exit'): ")
        if query.lower() in ['exit', 'quit']:
            break
        response = qa_chain.run(query)
        print("\nAnswer:", response["result"])
        print("Sources:")
        for doc in response["source_documents"]:
            print(f"- {doc.metadata}")

if __name__ == "__main__":
    main()