from pathlib import Path
import json
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_mitre_documents(json_path: str) -> list[Document]:
    with open(json_path, "r", encoding="utf-8") as f:
        stix_data = json.load(f)

    documents = []
    for obj in stix_data.get("objects", []):
        if obj.get("type") == "attack-pattern" and not obj.get("revoked", False):
            technique_id = next(
                (x.get("external_id") for x in obj.get("external_references", []) if "external_id" in x),
                None
            )
            content = f"""
Name: {obj.get('name')}
ID: {technique_id}
Description: {obj.get('description')}
Platforms: {", ".join(obj.get("x_mitre_platforms", []))}
Kill Chain Phases: {", ".join(x['phase_name'] for x in obj.get('kill_chain_phases', [])) if obj.get('kill_chain_phases') else "N/A"}
Tactic Types: {", ".join(obj.get("x_mitre_tactic_type", [])) if obj.get("x_mitre_tactic_type") else "N/A"}
""".strip()
            documents.append(Document(page_content=content, metadata={
                "source": "MITRE ATT&CK",
                "technique_id": technique_id
            }))
    return documents

def load_excel(file_path: Path) -> list[Document]:
    df = pd.read_excel(file_path)
    documents = []
    for i, row in df.iterrows():
        row_text = "\n".join([f"{col}: {row[col]}" for col in df.columns if pd.notnull(row[col])])
        metadata = {"source": str(file_path.name), "row_index": i}
        documents.append(Document(page_content=row_text, metadata=metadata))
    return documents

def load_documents(folder_path: str) -> list[Document]:
    documents = []
    folder = Path(folder_path)

    for file_path in folder.iterdir():
        suffix = file_path.suffix.lower()
        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(str(file_path))
                documents.extend(loader.load())

            elif suffix == ".xlsx":
                documents.extend(load_excel(file_path))

            elif suffix == ".json" and "attack" in file_path.name.lower():
                documents.extend(load_mitre_documents(str(file_path)))

            else:
                print(f"[INFO] Ignored unsupported file: {file_path.name}")
        except Exception as e:
            print(f"[WARN] Error processing {file_path.name}: {e}")

    return documents

def chunk_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(docs)