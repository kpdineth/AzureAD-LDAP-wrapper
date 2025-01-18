from sentence_transformers import SentenceTransformer
from typing import List, Dict
import re

class CodeEmbeddings:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the code embeddings model."""
        self.model = SentenceTransformer(model_name)
        
    def preprocess_code(self, code: str) -> str:
        """Preprocess Pronto 4GL code for better embedding."""
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        return code.strip()
        
    def encode_code(self, code_snippets: List[str]) -> List:
        """Generate embeddings for code snippets."""
        processed_snippets = [self.preprocess_code(snippet) for snippet in code_snippets]
        return self.model.encode(processed_snippets, show_progress_bar=False)
    
    def encode_query(self, query: str) -> List:
        """Generate embedding for query."""
        return self.model.encode([query], show_progress_bar=False)[0]
    
    def get_similar_snippets(self, query: str, code_snippets: List[str], top_k: int = 3) -> List[Dict]:
        """Find most similar code snippets to query."""
        query_embedding = self.encode_query(query)
        code_embeddings = self.encode_code(code_snippets)
        
        # Calculate similarities and return top matches
        similarities = []
        for i, code_embedding in enumerate(code_embeddings):
            similarity = self.cosine_similarity(query_embedding, code_embedding)
            similarities.append({
                'code': code_snippets[i],
                'similarity': similarity
            })
        
        return sorted(similarities, key=lambda x: x['similarity'], reverse=True)[:top_k]
    
    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
