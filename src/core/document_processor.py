"""Document processor for Pronto 4GL Assistant."""
import re
from typing import Dict, List
from datetime import datetime

class Pronto4GLProcessor:
    """Handles Pronto 4GL document processing and validation."""
    
    def __init__(self):
        """Initialize the document processor."""
        self.supported_extensions = {'.4gl', '.txt', '.md'}
        
    def validate_file(self, filename: str) -> bool:
        """Validate file type and format.
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        return any(filename.lower().endswith(ext) for ext in self.supported_extensions)
    
    def process_document(self, content: str) -> Dict:
        """Process a Pronto 4GL document.
        
        Args:
            content: Document content to process
            
        Returns:
            Dict: Processed document with metadata and chunks
        """
        # Extract metadata
        metadata = self._extract_metadata(content)
        
        # Split into chunks
        chunks = self._split_into_chunks(content)
        
        return {
            "metadata": metadata,
            "chunks": chunks,
            "suggestions": self._generate_suggestions(content)
        }
    
    def _extract_metadata(self, content: str) -> Dict:
        """Extract metadata from document content.
        
        Args:
            content: Document content
            
        Returns:
            Dict: Extracted metadata
        """
        lines = content.split('\n')
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "size_bytes": len(content.encode('utf-8')),
            "line_count": len(lines),
            "function_count": len(re.findall(r'\bFUNCTION\b', content, re.IGNORECASE)),
            "has_comments": bool(re.search(r'#.*$', content, re.MULTILINE))
        }
        
        # Extract any module or function documentation
        doc_match = re.search(r'#\s*(.+?)(?=\n[^#]|\Z)', content)
        if doc_match:
            metadata["documentation"] = doc_match.group(1).strip()
            
        return metadata
    
    def _split_into_chunks(self, content: str, chunk_size: int = 512) -> List[str]:
        """Split document into processable chunks.
        
        Args:
            content: Document content
            chunk_size: Target size for each chunk
            
        Returns:
            List[str]: Document chunks
        """
        chunks = []
        
        # First split by functions
        functions = re.split(r'(?i)(FUNCTION\s+[^\n]+)', content)
        current_chunk = ""
        
        for part in functions:
            if not part.strip():
                continue
                
            # If adding this part would exceed chunk size, store current chunk
            if len(current_chunk) + len(part) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            current_chunk += part + "\n"
        
        # Add any remaining content
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks
    
    def _generate_suggestions(self, content: str) -> List[Dict]:
        """Generate code improvement suggestions.
        
        Args:
            content: Document content
            
        Returns:
            List[Dict]: List of suggestions
        """
        suggestions = []
        
        # Check for missing documentation
        if not re.search(r'#.*$', content, re.MULTILINE):
            suggestions.append({
                "type": "documentation",
                "message": "Consider adding documentation comments",
                "severity": "low"
            })
        
        # Check for SQL injection risks
        if re.search(r'SELECT.*WHERE.*=\s*:', content, re.IGNORECASE | re.MULTILINE):
            suggestions.append({
                "type": "security",
                "message": "Verify SQL query parameters are properly sanitized",
                "severity": "high"
            })
        
        # Check for error handling
        if not re.search(r'IF\s+sqlca\.sqlcode', content, re.IGNORECASE):
            suggestions.append({
                "type": "reliability",
                "message": "Add SQL error handling",
                "severity": "medium"
            })
            
        return suggestions
