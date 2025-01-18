import chromadb

class VectorStore:
    def __init__(self, collection_name: str = "pronto_4gl"):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(name=collection_name)
    
    def add_documents(self, documents: list, metadatas: list = None):
        """Add documents to vector store."""
        # TODO: Implement document addition with embeddings
        pass
    
    def search(self, query: str, n_results: int = 3):
        """Search for similar documents."""
        # TODO: Implement similarity search
        pass
