from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

def build_rag_chain(vectordb):
    retriever = vectordb.as_retriever()

    model_id = "tiiuae/falcon-rw-1b"  # Local, free, small model
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1,
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7,
    )

    llm = HuggingFacePipeline(pipeline=pipe)
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)