from typing import List, Dict, Optional
import subprocess
import os

def run_terminal_command(command: List[str]) -> Dict:
    """Run a terminal command and return the result."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "status": "success",
            "output": result.stdout,
            "error": result.stderr
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "output": e.stdout,
            "error": e.stderr
        }

def validate_file_size(file_path: str, max_size_mb: int = 10) -> bool:
    """Validate if file size is within limits."""
    try:
        size = os.path.getsize(file_path)
        return size <= max_size_mb * 1024 * 1024
    except OSError:
        return False

def format_code_suggestion(suggestion: Dict) -> str:
    """Format code suggestion for terminal output."""
    return f"""
Type: {suggestion.get('type', 'Unknown')}
Location: Line {suggestion.get('line', 'N/A')}
Message: {suggestion.get('message', '')}
Severity: {suggestion.get('severity', 'medium')}
"""

def format_code_analysis(analysis: Dict) -> str:
    """Format code analysis for terminal output."""
    return f"""
Code Quality Score: {analysis.get('code_quality', 'N/A')}/10
Explanation: {analysis.get('explanation', '')}

Suggestions:
{'-' * 40}
{''.join(format_code_suggestion(s) for s in analysis.get('suggestions', []))}
"""
