"""Database manager for Pronto 4GL Assistant."""
import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Optional
import os
from datetime import datetime

class DatabaseManager:
    """Manages all database operations for the application."""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """Initialize database connection.
        
        Args:
            persist_directory: Optional directory for persistence. If None, uses in-memory storage.
        """
        self.logger = logging.getLogger(__name__)
        
        # Configure ChromaDB
        settings = Settings(
            allow_reset=True,
            anonymized_telemetry=False
        )
        
        if persist_directory:
            os.makedirs(persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=settings
            )
            self.logger.info(f"Using persistent storage at {persist_directory}")
        else:
            self.client = chromadb.Client(settings)
            self.logger.info("Using in-memory storage")
        
        # Initialize collections
        self.code_collection = self.client.get_or_create_collection(
            name="pronto4gl_code",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.documents_collection = self.client.get_or_create_collection(
            name="pronto4gl_documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_code_snippet(self, code: str, metadata: Dict, embedding: List[float]) -> str:
        """Add a code snippet to the database.
        
        Args:
            code: The code snippet text
            metadata: Additional information about the code
            embedding: Vector representation of the code
            
        Returns:
            str: ID of the stored code snippet
        """
        try:
            timestamp = datetime.now().isoformat()
            doc_id = f"code_{timestamp}"
            
            # Update metadata with timestamp
            metadata.update({"timestamp": timestamp})
            
            self.code_collection.add(
                documents=[code],
                metadatas=[metadata],
                embeddings=[embedding],
                ids=[doc_id]
            )
            return doc_id
        except Exception as e:
            self.logger.error(f"Error adding code snippet: {str(e)}")
            raise
    
    def add_document(self, content: str, metadata: Dict, embedding: List[float]) -> str:
        """Add a document to the database.
        
        Args:
            content: The document content
            metadata: Document metadata (filename, size, etc.)
            embedding: Vector representation of the document
            
        Returns:
            str: ID of the stored document
        """
        try:
            timestamp = datetime.now().isoformat()
            doc_id = f"doc_{metadata.get('filename', 'unknown')}_{timestamp}"
            
            # Update metadata with timestamp
            metadata.update({
                "timestamp": timestamp,
                "size_bytes": len(content.encode('utf-8'))
            })
            
            self.documents_collection.add(
                documents=[content],
                metadatas=[metadata],
                embeddings=[embedding],
                ids=[doc_id]
            )
            return doc_id
        except Exception as e:
            self.logger.error(f"Error adding document: {str(e)}")
            raise
    
    def query_similar_code(self, query_embedding: List[float], n_results: int = 3) -> List[Dict]:
        """Find similar code snippets.
        
        Args:
            query_embedding: Vector representation of the query
            n_results: Number of results to return
            
        Returns:
            List[Dict]: Similar code snippets with metadata
        """
        try:
            print(f"[DEBUG] Starting similar code query with n_results={n_results}")
            print(f"[DEBUG] Query embedding shape: {len(query_embedding)}")
            print(f"[DEBUG] Query embedding values: {query_embedding[:5]}...")
            
            print("[DEBUG] Checking collection status...")
            collection_stats = self.code_collection.count()
            print(f"[DEBUG] Collection has {collection_stats} documents")
            
            print("[DEBUG] Executing similarity search...")
            results = self.code_collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, max(1, collection_stats))
            )
            print(f"[DEBUG] Found {len(results['documents'][0])} similar code snippets")
            print(f"[DEBUG] First result distance: {results['distances'][0][0] if results['distances'][0] else 'N/A'}")
            print("[DEBUG] Query complete")
            
            return [{
                'code': doc,
                'metadata': meta,
                'distance': dist
            } for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )]
        except Exception as e:
            self.logger.error(f"Error querying similar code: {str(e)}")
            raise
    
    def query_similar_documents(self, query_embedding: List[float], n_results: int = 3) -> List[Dict]:
        """Find similar documents.
        
        Args:
            query_embedding: Vector representation of the query
            n_results: Number of results to return
            
        Returns:
            List[Dict]: Similar documents with metadata
        """
        try:
            results = self.documents_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return [{
                'content': doc,
                'metadata': meta,
                'distance': dist
            } for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )]
        except Exception as e:
            self.logger.error(f"Error querying similar documents: {str(e)}")
            raise
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict]:
        """Retrieve a document by its ID.
        
        Args:
            doc_id: The document identifier
            
        Returns:
            Optional[Dict]: Document data if found, None otherwise
        """
        try:
            result = self.documents_collection.get(
                ids=[doc_id],
                include=['documents', 'metadatas']
            )
            
            if result['documents']:
                return {
                    'content': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving document: {str(e)}")
            raise
    
    def get_code_by_id(self, code_id: str) -> Optional[Dict]:
        """Retrieve a code snippet by its ID.
        
        Args:
            code_id: The code snippet identifier
            
        Returns:
            Optional[Dict]: Code data if found, None otherwise
        """
        try:
            result = self.code_collection.get(
                ids=[code_id],
                include=['documents', 'metadatas']
            )
            
            if result['documents']:
                return {
                    'code': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving code: {str(e)}")
            raise
    
    def reset(self):
        """Reset the database (mainly for testing)."""
        try:
            self.client.reset()
            # Reinitialize collections
            self.code_collection = self.client.get_or_create_collection(
                name="pronto4gl_code",
                metadata={"hnsw:space": "cosine"}
            )
            self.documents_collection = self.client.get_or_create_collection(
                name="pronto4gl_documents",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            self.logger.error(f"Error resetting database: {str(e)}")
            raise
