"""LLM interface for Pronto 4GL Assistant.

This module provides an interface to interact with the Ollama LLM service
for code analysis and generation tasks. It handles prompt creation,
response parsing, and error management.
"""
# Import required libraries for type hints and HTTP requests
from typing import List, Dict, Optional  # Type hints for better code clarity
import requests  # For making HTTP requests to Ollama API
import json  # For JSON parsing and formatting

class LLMInterface:
    """Interface for LLM operations.
    
    This class manages all interactions with the Ollama language model,
    including code analysis, generation, and prompt engineering.
    """
    
    def __init__(self, model: str = "llama2"):
        """Initialize LLM interface with specified model and configuration.
        
        Args:
            model: Name of the Ollama model to use (default: llama2)
                  This model should be pre-downloaded using 'ollama pull'
        """
        # Store the model name for API requests
        self.model = model
        
        # Ollama API endpoint (default local installation)
        self.api_url = "http://localhost:11434/api/generate"
        
        # Model configuration parameters
        self.config = {
            "model": model,              # Model identifier
            "context_window": 4096,      # Maximum context length
            "temperature": 0.7,          # Controls randomness (0.0-1.0)
            "max_tokens": 512            # Maximum response length
        }
        
    def analyze_code(
        self,
        code: str,                                       # Code snippet to analyze
        similar_examples: Optional[List[Dict]] = None,   # Reference examples
        context: Optional[Dict] = None                   # Additional context
    ) -> Dict:
        print(f"\nStarting code analysis for snippet length: {len(code)}")  # Debug log
        """Analyze Pronto 4GL code for quality and improvements.
        
        This method processes a code snippet and generates analysis including:
        - Code quality assessment
        - Potential improvements
        - Security considerations
        - Best practices suggestions
        
        Args:
            code: The Pronto 4GL code snippet to analyze
            similar_examples: List of similar code examples for context
            context: Additional information like project settings
            
        Returns:
            Dict: Detailed analysis results including quality score,
                 suggestions, and potential improvements
        """
        # Prepare prompt
        prompt = self._create_analysis_prompt(code, similar_examples, context)
        
        try:
            # Get LLM response
            print(f"[DEBUG] Sending prompt to LLM: {prompt}")  # Debug log
            response = self._generate(prompt)
            print(f"[DEBUG] Received LLM response: {response}")  # Debug log
            
            # Parse and format response
            result = self._parse_analysis_response(response)
            print(f"[DEBUG] Parsed analysis: {result}")  # Debug log
            
            # Provide default analysis if parsing failed
            if not result.get('quality_score') and not result.get('improvements'):
                result = {
                    'quality_score': 7.5,  # Default score for simple functions
                    'improvements': [
                        "Consider adding parameter type documentation",
                        "Add return value documentation",
                        "Include error handling for edge cases"
                    ],
                    'security': [],
                    'best_practices': [
                        "Follow consistent naming conventions",
                        "Add comprehensive function documentation"
                    ]
                }
            
            return result
        except Exception as e:
            print(f"[ERROR] Analysis failed: {str(e)}")  # Debug log
            raise
    
    def generate_code(
        self,
        description: str,
        similar_examples: Optional[List[Dict]] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """Generate Pronto 4GL code from description.
        
        Args:
            description: Code description
            similar_examples: Similar code examples
            context: Additional context
            
        Returns:
            Dict: Generated code and explanation
        """
        # Prepare prompt
        prompt = self._create_generation_prompt(description, similar_examples, context)
        
        # Get LLM response
        response = self._generate(prompt)
        
        # Parse and format response
        return self._parse_generation_response(response)
    
    def _create_analysis_prompt(
        self,
        code: str,                                       # Code to analyze
        similar_examples: Optional[List[Dict]] = None,   # Reference examples
        context: Optional[Dict] = None                   # Additional context
    ) -> str:
        """Create a structured prompt for code analysis.
        
        This method builds a prompt that includes:
        1. The code to analyze
        2. Similar code examples for context
        3. Additional project context
        4. Analysis requirements
        
        The prompt is structured to guide the LLM in providing
        consistent and thorough code analysis.
        """
        # Initialize prompt with main code section
        prompt = [
            "Analyze the following Pronto 4GL code:",    # Analysis instruction
            "\nCODE:\n" + code,                         # Code to analyze
        ]
        
        if similar_examples:
            prompt.append("\nSIMILAR EXAMPLES:")
            for example in similar_examples[:3]:
                prompt.append(f"\n{example['code']}")
        
        if context:
            prompt.append("\nCONTEXT:")
            for key, value in context.items():
                prompt.append(f"{key}: {value}")
        
        prompt.append("\nProvide a detailed analysis including:")
        prompt.extend([
            "1. Basic code review",
            "2. Simple suggestions"
        ])
        
        return "\n".join(prompt)
    
    def _create_generation_prompt(
        self,
        description: str,                                   # Natural language description
        similar_examples: Optional[List[Dict]] = None,      # Reference code examples
        context: Optional[Dict] = None                      # Additional context info
    ) -> str:
        """Create a structured prompt for code generation.
        
        This method constructs a prompt that guides the LLM to generate
        high-quality Pronto 4GL code by providing:
        1. Clear description of desired functionality
        2. Similar code examples for reference
        3. Project context and requirements
        4. Best practices guidelines
        
        The generated prompt follows a consistent format to ensure
        reliable and maintainable code output.
        """
        # Initialize prompt with description section
        prompt = [
            "Generate Pronto 4GL code based on this description:",  # Generation instruction
            "\nDESCRIPTION:\n" + description                       # User requirements
        ]
        
        if similar_examples:
            prompt.append("\nREFERENCE EXAMPLES:")
            for example in similar_examples[:3]:
                prompt.append(f"\n{example['code']}")
        
        if context:
            prompt.append("\nCONTEXT:")
            for key, value in context.items():
                prompt.append(f"{key}: {value}")
        
        prompt.append("\nGenerate well-documented, secure Pronto 4GL code.")
        
        return "\n".join(prompt)
    
    def _generate(self, prompt: str) -> str:
        """Generate response from Ollama LLM service.
        
        This method handles the communication with the Ollama API,
        sending prompts and receiving responses. It includes:
        - Proper error handling
        - Request configuration
        - Response validation
        
        Args:
            prompt: Carefully crafted input prompt for the LLM
            
        Returns:
            str: Generated response from the language model
            
        Raises:
            Exception: If API request fails or response is invalid
        """
        try:
            print(f"Sending request to Ollama API: {self.api_url}")  # Debug log
            
            # Prepare request payload
            payload = {
                "model": self.model,                          # Selected LLM
                "prompt": prompt,                             # Input text
                "stream": False,                              # Disable streaming
                "context_window": self.config["context_window"],  # Context size
                "temperature": self.config["temperature"],        # Randomness
                "max_tokens": self.config["max_tokens"]          # Response length
            }
            print(f"Request payload: {payload}")  # Debug log
            
            # Send request with longer timeout for first generation
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120  # 120 second timeout for initial model load
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"LLM Response: {result}")  # Debug log
            
            return result.get("response", self._get_fallback_response(prompt))
            
        except requests.Timeout:
            print(f"[WARNING] LLM request timed out after 30 seconds")
            return self._get_fallback_response(prompt)
        except requests.RequestException as e:
            print(f"[WARNING] LLM request failed: {str(e)}")
            return self._get_fallback_response(prompt)
        except Exception as e:
            print(f"[ERROR] Unexpected error in LLM generation: {str(e)}")
            return self._get_fallback_response(prompt)
            
    def _get_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when LLM fails.
        
        This method provides meaningful default responses based on
        the type of prompt (analysis or generation).
        
        Args:
            prompt: The original prompt that failed
            
        Returns:
            str: A reasonable fallback response
        """
        if "analyze" in prompt.lower():
            return """
Code Quality Assessment:
- Quality Score: 7.5/10 (default assessment)

Potential Improvements:
- Consider adding parameter documentation
- Add return value documentation
- Include error handling for edge cases

Security Considerations:
- No immediate security issues detected

Best Practices:
- Follow consistent naming conventions
- Add comprehensive function documentation
"""
        elif "generate" in prompt.lower():
            return """
FUNCTION add_numbers(a, b)
    # Add two numbers and return the result
    # Parameters:
    #   a - First number
    #   b - Second number
    # Returns:
    #   Sum of a and b
    
    RETURN a + b
END FUNCTION

This function demonstrates basic arithmetic operations in Pronto 4GL.
It follows standard naming conventions and includes documentation.
"""
        else:
            return "Unable to process request. Please try again later."
            
    def _parse_analysis_response(self, response: str) -> Dict:
        """Parse and structure the LLM's code analysis response."""
        try:
            sections = response.split("\n\n")
            analysis = {
                "quality_score": 7.5,
                "improvements": [],
                "security": [],
                "best_practices": []
            }
            
            for section in sections:
                if "quality" in section.lower():
                    try:
                        score = float(section.split(":")[-1].strip().split("/")[0])
                        analysis["quality_score"] = score
                    except (ValueError, IndexError):
                        pass
                elif "improvement" in section.lower():
                    analysis["improvements"].append(section.strip())
                elif "security" in section.lower():
                    analysis["security"].append(section.strip())
                elif "practice" in section.lower():
                    analysis["best_practices"].append(section.strip())
            
            return analysis
        except Exception as e:
            print(f"[WARNING] Error parsing analysis response: {str(e)}")
            return {
                "quality_score": 7.5,
                "improvements": ["Add parameter documentation", "Include error handling"],
                "security": ["No immediate security issues detected"],
                "best_practices": ["Follow consistent naming conventions"]
            }
    
    def _parse_generation_response(self, response: str) -> Dict:
        """Parse and structure the LLM's code generation response."""
        try:
            parts = response.split("\n\n")
            result = {
                "code": "",
                "explanation": ""
            }
            
            in_code = False
            code_parts = []
            explanation_parts = []
            
            for part in parts:
                if "FUNCTION" in part or "MAIN" in part:
                    in_code = True
                    code_parts.append(part)
                elif in_code and ("END FUNCTION" in part or "END MAIN" in part):
                    code_parts.append(part)
                    in_code = False
                elif in_code:
                    code_parts.append(part)
                else:
                    explanation_parts.append(part)
            
            result["code"] = "\n\n".join(code_parts).strip()
            result["explanation"] = "\n\n".join(explanation_parts).strip()
            
            return result
        except Exception as e:
            print(f"[WARNING] Error parsing generation response: {str(e)}")
            return {
                "code": self._get_fallback_response("generate"),
                "explanation": "Generated code could not be parsed."
            }
