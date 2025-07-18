# Updated import from the new package
from langchain_huggingface import HuggingFaceEmbeddings

def get_embedder():
    # Use a smaller model for free tier deployment
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )