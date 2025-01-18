import os
from typing import List, Dict, Optional
import chromadb
from ..core.document_processor import Pronto4GLProcessor
from ..core.embeddings import CodeEmbeddings

class Pronto4GLTrainer:
    def __init__(self, persist_directory: str = "data/chroma"):
        """Initialize the training system."""
        self.processor = Pronto4GLProcessor()
        self.embeddings = CodeEmbeddings()
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.chroma_client.get_or_create_collection(
            name="pronto4gl",
            metadata={"hnsw:space": "cosine"}
        )
        
    def train(self, code_directory: str) -> Dict:
        """Train the system with Pronto 4GL code files."""
        try:
            # Load and process documents
            documents = self.load_documents(code_directory)
            processed_docs = []
            
            # Process each document
            for doc in documents:
                processed = self.processor.process_document(doc["content"])
                processed["filepath"] = doc["filepath"]
                processed_docs.append(processed)
            
            # Create embeddings and store in ChromaDB
            self._store_embeddings(processed_docs)
            
            return {
                "status": "success",
                "documents_processed": len(processed_docs),
                "chunks_created": sum(len(doc["chunks"]) for doc in processed_docs)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def load_documents(self, directory: str) -> List[Dict]:
        """Load Pronto 4GL documents from directory."""
        documents = []
        for root, _, files in os.walk(directory):
            for file in files:
                if self.processor.validate_file(file):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if len(content.encode('utf-8')) <= 10 * 1024 * 1024:  # 10MB limit
                                documents.append({
                                    "filepath": filepath,
                                    "content": content
                                })
                    except Exception as e:
                        print(f"Error loading {filepath}: {str(e)}")
        return documents
    
    def _store_embeddings(self, processed_docs: List[Dict]) -> None:
        """Store document embeddings in ChromaDB."""
        for doc in processed_docs:
            chunks = doc["chunks"]
            embeddings = self.embeddings.encode_code(chunks)
            
            # Prepare metadata for each chunk
            metadata_list = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    "filepath": doc["filepath"],
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                metadata.update(doc["metadata"])
                metadata_list.append(metadata)
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadata_list,
                ids=[f"{os.path.basename(doc['filepath'])}_{i}" for i in range(len(chunks))]
            )
    
    def query_similar(self, query: str, top_k: int = 3) -> List[Dict]:
        """Query similar code snippets."""
        query_embedding = self.embeddings.encode_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return [{
            "document": doc,
            "metadata": meta
        } for doc, meta in zip(results["documents"][0], results["metadatas"][0])]
