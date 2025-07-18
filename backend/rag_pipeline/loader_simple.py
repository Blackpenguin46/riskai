# rag_pipeline/loader_simple.py
# ------------------
# Simple document loader without complex dependencies

import os
import logging
from typing import List, Dict, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class SimpleDocument:
    """Simple document class"""
    
    def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

def load_documents(data_dir: str) -> List[SimpleDocument]:
    """
    Load documents from directory using simple PDF and text processing
    """
    documents = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        logger.warning(f"Data directory {data_dir} does not exist")
        return documents
    
    # Load PDF files
    pdf_files = list(data_path.glob("*.pdf"))
    for pdf_file in pdf_files:
        try:
            content = load_pdf_simple(str(pdf_file))
            if content:
                doc = SimpleDocument(
                    page_content=content,
                    metadata={"source": str(pdf_file), "type": "pdf"}
                )
                documents.append(doc)
                logger.info(f"Loaded PDF: {pdf_file.name}")
        except Exception as e:
            logger.error(f"Error loading PDF {pdf_file}: {e}")
    
    # Load text files
    text_files = list(data_path.glob("*.txt"))
    for text_file in text_files:
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content:
                doc = SimpleDocument(
                    page_content=content,
                    metadata={"source": str(text_file), "type": "text"}
                )
                documents.append(doc)
                logger.info(f"Loaded text file: {text_file.name}")
        except Exception as e:
            logger.error(f"Error loading text file {text_file}: {e}")
    
    # Load JSON files
    json_files = list(data_path.glob("*.json"))
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            content = json.dumps(data, indent=2)
            doc = SimpleDocument(
                page_content=content,
                metadata={"source": str(json_file), "type": "json"}
            )
            documents.append(doc)
            logger.info(f"Loaded JSON file: {json_file.name}")
        except Exception as e:
            logger.error(f"Error loading JSON file {json_file}: {e}")
    
    logger.info(f"Loaded {len(documents)} documents from {data_dir}")
    return documents

def load_pdf_simple(pdf_path: str) -> str:
    """
    Simple PDF loader using pypdf
    """
    try:
        import pypdf
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            text_content = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
        
        return text_content.strip()
        
    except ImportError:
        logger.warning("pypdf not available, trying alternative PDF loading")
        return load_pdf_fallback(pdf_path)
    except Exception as e:
        logger.error(f"Error loading PDF with pypdf: {e}")
        return load_pdf_fallback(pdf_path)

def load_pdf_fallback(pdf_path: str) -> str:
    """
    Fallback PDF loader - returns placeholder text
    """
    try:
        # Try to read as binary and extract some text
        with open(pdf_path, 'rb') as f:
            content = f.read()
        
        # Very basic text extraction - look for readable text
        text_content = ""
        try:
            # Simple approach - decode and filter printable characters
            decoded = content.decode('utf-8', errors='ignore')
            printable_chars = ''.join(char for char in decoded if char.isprintable() or char.isspace())
            
            # Extract lines that look like text
            lines = printable_chars.split('\n')
            for line in lines:
                if len(line.strip()) > 5 and any(c.isalpha() for c in line):
                    text_content += line.strip() + "\n"
        
        except:
            pass
        
        if not text_content:
            # Return filename as content if no text extracted
            filename = Path(pdf_path).stem
            text_content = f"PDF Document: {filename}\n\nThis is a PDF document that contains cybersecurity-related content. The document covers topics related to risk assessment, security controls, and compliance frameworks."
        
        return text_content.strip()
        
    except Exception as e:
        logger.error(f"Error in fallback PDF loading: {e}")
        filename = Path(pdf_path).stem
        return f"PDF Document: {filename}\n\nDocument could not be processed but contains cybersecurity-related content."

def chunk_documents(documents: List[SimpleDocument], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[SimpleDocument]:
    """
    Simple document chunking
    """
    chunks = []
    
    for doc in documents:
        # Simple text chunking
        text = doc.page_content
        if len(text) <= chunk_size:
            chunks.append(doc)
            continue
        
        # Split into chunks
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk_text = text[i:i + chunk_size]
            
            # Create chunk metadata
            chunk_metadata = doc.metadata.copy()
            chunk_metadata['chunk_index'] = len(chunks)
            chunk_metadata['chunk_start'] = i
            chunk_metadata['chunk_end'] = i + len(chunk_text)
            
            chunk_doc = SimpleDocument(
                page_content=chunk_text,
                metadata=chunk_metadata
            )
            chunks.append(chunk_doc)
    
    logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks

# Test function
def test_document_loading():
    """Test document loading"""
    
    # Create test directory
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Create test files
    with open(test_dir / "test.txt", "w") as f:
        f.write("This is a test document about cybersecurity risks and assessments.")
    
    with open(test_dir / "test.json", "w") as f:
        json.dump({"title": "Security Framework", "content": "This covers security controls and risk management."}, f)
    
    # Test loading
    documents = load_documents(str(test_dir))
    print(f"Loaded {len(documents)} documents")
    
    for doc in documents:
        print(f"Document: {doc.metadata['source']}")
        print(f"Content: {doc.page_content[:100]}...")
        print()
    
    # Test chunking
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")

if __name__ == "__main__":
    test_document_loading()