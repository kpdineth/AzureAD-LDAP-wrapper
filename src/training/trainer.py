"""Training system for Pronto 4GL Assistant."""
import os
from typing import List, Dict, Optional
from ..core.document_processor import Pronto4GLProcessor
from ..core.embeddings import CodeEmbeddings
from ..core.database import DatabaseManager

class Pronto4GLTrainer:
    """Manages system training with code examples."""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """Initialize the training system.
        
        Args:
            persist_directory: Optional directory for data persistence
        """
        self.processor = Pronto4GLProcessor()
        self.embeddings = CodeEmbeddings()
        self.db = DatabaseManager(persist_directory)
    
    def train(self, code_directory: str) -> Dict:
        """Train the system with Pronto 4GL code files.
        
        Args:
            code_directory: Directory containing code files
            
        Returns:
            Dict: Training results summary
        """
        try:
            # Load and process documents
            documents = self.load_documents(code_directory)
            processed_docs = []
            
            # Process each document
            for doc in documents:
                processed = self.processor.process_document(doc["content"])
                processed["filepath"] = doc["filepath"]
                processed_docs.append(processed)
            
            # Generate embeddings and store in database
            total_chunks = 0
            for doc in processed_docs:
                chunks = doc["chunks"]
                embeddings = self.embeddings.encode_code(chunks)
                
                # Store each chunk with its metadata
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    metadata = {
                        "filepath": doc["filepath"],
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                    metadata.update(doc["metadata"])
                    
                    self.db.add_code_snippet(
                        code=chunk,
                        metadata=metadata,
                        embedding=embedding
                    )
                total_chunks += len(chunks)
            
            return {
                "status": "success",
                "documents_processed": len(processed_docs),
                "chunks_created": total_chunks
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def load_documents(self, directory: str) -> List[Dict]:
        """Load Pronto 4GL documents from directory.
        
        Args:
            directory: Path to code directory
            
        Returns:
            List[Dict]: Loaded documents with metadata
        """
        documents = []
        for root, _, files in os.walk(directory):
            for file in files:
                if self.processor.validate_file(file):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Check file size (1GB limit)
                            if len(content.encode('utf-8')) <= 1024 * 1024 * 1024:
                                documents.append({
                                    "filepath": filepath,
                                    "content": content
                                })
                    except Exception as e:
                        print(f"Error loading {filepath}: {str(e)}")
        return documents
    
    def query_similar(self, query: str, top_k: int = 3) -> List[Dict]:
        """Query similar code examples.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List[Dict]: Similar code examples
        """
        query_embedding = self.embeddings.encode_query(query)
        return self.db.query_similar_code(query_embedding, top_k)
