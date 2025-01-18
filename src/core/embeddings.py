"""Code embeddings manager for Pronto 4GL Assistant."""
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import re

class CodeEmbeddings:
    """Manages code vector embeddings generation."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the code embeddings model.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        print(f"Initializing CodeEmbeddings with model: {model_name}")  # Debug log
        try:
            self.model = SentenceTransformer(model_name)
            print("SentenceTransformer model loaded successfully")  # Debug log
        except Exception as e:
            print(f"Error loading SentenceTransformer model: {str(e)}")  # Debug log
            raise
    
    def preprocess_code(self, code: str) -> str:
        """Preprocess Pronto 4GL code for better embedding.
        
        Args:
            code: Code snippet to preprocess
            
        Returns:
            str: Preprocessed code
        """
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        
        # Normalize function declarations
        code = re.sub(r'(?i)FUNCTION\s+', 'FUNCTION ', code)
        
        return code.strip()
    
    def encode_code(self, code_snippets: List[str]) -> List[List[float]]:
        """Generate embeddings for code snippets.
        
        Args:
            code_snippets: List of code snippets
            
        Returns:
            List[List[float]]: List of embeddings
        """
        try:
            print(f"[DEBUG] Encoding {len(code_snippets)} code snippets")
            print(f"[DEBUG] Code snippets to process: {code_snippets}")
            
            processed_snippets = [self.preprocess_code(snippet) for snippet in code_snippets]
            print(f"[DEBUG] Processed snippets: {processed_snippets}")
            print("[DEBUG] Code preprocessing complete")
            
            print("[DEBUG] Starting embedding generation...")
            embeddings = self.model.encode(processed_snippets, show_progress_bar=True)
            print(f"[DEBUG] Successfully generated {len(embeddings)} embeddings")
            print(f"[DEBUG] First embedding shape: {len(embeddings[0])}")
            return embeddings
        except Exception as e:
            print(f"Error encoding code snippets: {str(e)}")  # Debug log
            raise
    
    def encode_query(self, query: str) -> List[float]:
        """Generate embedding for search query.
        
        Args:
            query: Search query
            
        Returns:
            List[float]: Query embedding
        """
        return self.model.encode([query], show_progress_bar=False)[0]
    
    def get_similar_snippets(self, query: str, code_snippets: List[str], top_k: int = 3) -> List[Dict]:
        """Find most similar code snippets to query.
        
        Args:
            query: Search query
            code_snippets: List of code snippets to search
            top_k: Number of results to return
            
        Returns:
            List[Dict]: Similar code snippets with similarity scores
        """
        query_embedding = self.encode_query(query)
        code_embeddings = self.encode_code(code_snippets)
        
        # Calculate similarities
        similarities = []
        for i, code_embedding in enumerate(code_embeddings):
            similarity = self._cosine_similarity(query_embedding, code_embedding)
            similarities.append({
                'code': code_snippets[i],
                'similarity': similarity
            })
        
        # Sort by similarity and return top_k
        return sorted(similarities, key=lambda x: x['similarity'], reverse=True)[:top_k]
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            v1: First vector
            v2: Second vector
            
        Returns:
            float: Cosine similarity score
        """
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
