class Pronto4GLProcessor:
    def __init__(self):
        self.supported_extensions = [".4gl", ".txt", ".md"]
        self.code_patterns = {
            "function": r"FUNCTION\s+([a-zA-Z0-9_]+)\s*\((.*?)\)",
            "procedure": r"PROCEDURE\s+([a-zA-Z0-9_]+)\s*\((.*?)\)",
            "variable": r"DEFINE\s+([a-zA-Z0-9_]+)\s+AS\s+([a-zA-Z0-9_]+)",
            "sql": r"(SELECT|INSERT|UPDATE|DELETE)\s+.*?(?:;|$)",
            "comment": r"#.*$",
            "error_handling": r"TRY\s.*?CATCH"
        }
    
    def validate_file(self, filename: str) -> bool:
        return any(filename.endswith(ext) for ext in self.supported_extensions)
    
    def process_document(self, content: str) -> dict:
        """Process Pronto 4GL document content with detailed analysis."""
        chunks = self._chunk_content(content)
        code_elements = self._analyze_code(content)
        suggestions = self._generate_suggestions(content)
        
        return {
            "chunks": chunks,
            "metadata": self._extract_metadata(content),
            "code_elements": code_elements,
            "suggestions": suggestions
        }
    
    def _analyze_code(self, content: str) -> dict:
        """Analyze Pronto 4GL code structure and patterns."""
        lines = content.split('\n')
        analysis = {
            "functions": [],
            "procedures": [],
            "variables": [],
            "sql_queries": [],
            "error_handling": False,
            "documentation": self._has_documentation(content)
        }
        
        for i, line in enumerate(lines):
            # Find functions
            if match := re.search(self.code_patterns["function"], line):
                analysis["functions"].append({
                    "name": match.group(1),
                    "parameters": match.group(2),
                    "line": i + 1
                })
            
            # Find procedures
            if match := re.search(self.code_patterns["procedure"], line):
                analysis["procedures"].append({
                    "name": match.group(1),
                    "parameters": match.group(2),
                    "line": i + 1
                })
            
            # Find variables
            if match := re.search(self.code_patterns["variable"], line):
                analysis["variables"].append({
                    "name": match.group(1),
                    "type": match.group(2),
                    "line": i + 1
                })
            
            # Find SQL queries
            if match := re.search(self.code_patterns["sql"], line):
                analysis["sql_queries"].append({
                    "type": match.group(1),
                    "line": i + 1,
                    "query": line.strip()
                })
            
            # Check error handling
            if re.search(self.code_patterns["error_handling"], line):
                analysis["error_handling"] = True
        
        return analysis
    
    def _generate_suggestions(self, content: str) -> list:
        """Generate code improvement suggestions."""
        suggestions = []
        analysis = self._analyze_code(content)
        
        # Check error handling
        if not analysis["error_handling"]:
            suggestions.append({
                "type": "missing_error_handling",
                "message": "Add error handling using TRY-CATCH blocks",
                "severity": "high"
            })
        
        # Check documentation
        if not analysis["documentation"]:
            suggestions.append({
                "type": "missing_documentation",
                "message": "Add documentation comments to explain code functionality",
                "severity": "medium"
            })
        
        # Check SQL queries
        for query in analysis["sql_queries"]:
            if not self._validate_sql_query(query["query"]):
                suggestions.append({
                    "type": "sql_improvement",
                    "message": f"Improve SQL query structure at line {query['line']}",
                    "severity": "medium",
                    "line": query["line"]
                })
        
        return suggestions
    
    def _validate_sql_query(self, query: str) -> bool:
        """Validate SQL query structure."""
        query = query.upper()
        if query.startswith("SELECT") and "FROM" not in query:
            return False
        if query.startswith("INSERT") and ("INTO" not in query or "VALUES" not in query):
            return False
        if query.startswith("UPDATE") and "SET" not in query:
            return False
        if query.startswith("DELETE") and "FROM" not in query:
            return False
        return True
    
    def _has_documentation(self, content: str) -> bool:
        """Check if code has documentation comments."""
        lines = content.split('\n')
        comment_count = sum(1 for line in lines if re.match(self.code_patterns["comment"], line.strip()))
        return comment_count > 0
    
    def _chunk_content(self, content: str, chunk_size: int = 512):
        """Split content into chunks preserving code structure."""
        lines = content.split("\n")
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            # Start new chunk on function/procedure definition
            if re.search(r"(FUNCTION|PROCEDURE)\s+", line):
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_size = len(line.split())
                continue
            
            current_chunk.append(line)
            current_size += len(line.split())
            
            # Split on size or end of logical block
            if current_size >= chunk_size or line.strip() == "END":
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        
        return chunks
    
    def _extract_metadata(self, content: str) -> dict:
        """Extract detailed metadata from content."""
        analysis = self._analyze_code(content)
        return {
            "total_lines": len(content.split("\n")),
            "size_bytes": len(content.encode("utf-8")),
            "function_count": len(analysis["functions"]),
            "procedure_count": len(analysis["procedures"]),
            "variable_count": len(analysis["variables"]),
            "sql_query_count": len(analysis["sql_queries"]),
            "has_error_handling": analysis["error_handling"],
            "has_documentation": analysis["documentation"]
        }
