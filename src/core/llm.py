import requests
from typing import Dict, List, Optional
import json

class LLMInterface:
    def __init__(self, model: str = "llama2"):
        """Initialize LLM interface with Ollama."""
        self.base_url = "http://localhost:11434/api"
        self.model = model
        self.config = {
            "context_window": 4096,
            "temperature": 0.7,
            "max_tokens": 512
        }
        # Ensure config values are accessible as instance attributes
        self.temperature = self.config["temperature"]
        self.max_tokens = self.config["max_tokens"]
        self.context_window = self.config["context_window"]
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> Dict:
        """Generate response using Ollama."""
        url = f"{self.base_url}/generate"
        
        # Combine context and prompt if context is provided
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return {
                "response": response.json().get("response", ""),
                "status": "success"
            }
        except requests.exceptions.RequestException as e:
            return {
                "response": "",
                "status": "error",
                "error": str(e)
            }
    
    def analyze_code(self, code: str) -> Dict:
        """Analyze Pronto 4GL code and suggest improvements."""
        prompt = f"""Analyze the following Pronto 4GL code and suggest improvements:

{code}

Provide suggestions for:
1. Code structure
2. Error handling
3. Documentation
4. Performance
5. Best practices

Format the response as JSON with the following structure:
{{
    "suggestions": [
        {{"type": "improvement_type", "line": line_number, "message": "suggestion"}}
    ],
    "code_quality": "score 1-10",
    "explanation": "detailed explanation"
}}"""
        
        response = self.generate_response(prompt)
        if response["status"] == "success":
            try:
                return json.loads(response["response"])
            except json.JSONDecodeError:
                return {
                    "suggestions": [],
                    "code_quality": 0,
                    "explanation": "Failed to parse LLM response"
                }
        return {
            "suggestions": [],
            "code_quality": 0,
            "explanation": "Failed to generate analysis"
        }
    
    def generate_code(self, description: str, context: Optional[str] = None) -> Dict:
        """Generate Pronto 4GL code based on description."""
        prompt = f"""Generate Pronto 4GL code for the following requirement:

{description}

Requirements:
1. Include proper error handling with TRY-CATCH blocks
2. Add comprehensive documentation comments
3. Follow Pronto 4GL best practices
4. Include input validation
5. Optimize for performance

{f'Context:\n{context}' if context else ''}

Format the response as JSON with the following structure:
{{
    "code": "generated_code",
    "explanation": "explanation of the implementation",
    "usage_example": "example of how to use the code"
}}"""
        
        response = self.generate_response(prompt)
        if response["status"] == "success":
            try:
                return json.loads(response["response"])
            except json.JSONDecodeError:
                return {
                    "code": "",
                    "explanation": "Failed to parse LLM response",
                    "usage_example": ""
                }
        return {
            "code": "",
            "explanation": "Failed to generate code",
            "usage_example": ""
        }
    
    def suggest_edits(self, code: str, issue_description: Optional[str] = None) -> Dict:
        """Suggest specific edits for Pronto 4GL code."""
        prompt = f"""Suggest specific edits for the following Pronto 4GL code:

{code}

{f'Issue Description: {issue_description}' if issue_description else ''}

Provide specific edit suggestions with:
1. Line numbers
2. Current code
3. Suggested changes
4. Explanation for each change

Format the response as JSON with the following structure:
{{
    "edits": [
        {{
            "line_start": start_line,
            "line_end": end_line,
            "current_code": "code to replace",
            "suggested_code": "replacement code",
            "explanation": "why this change is needed"
        }}
    ],
    "overall_impact": "explanation of how these changes improve the code"
}}"""
        
        response = self.generate_response(prompt)
        if response["status"] == "success":
            try:
                return json.loads(response["response"])
            except json.JSONDecodeError:
                return {
                    "edits": [],
                    "overall_impact": "Failed to parse LLM response"
                }
        return {
            "edits": [],
            "overall_impact": "Failed to generate edit suggestions"
        }
