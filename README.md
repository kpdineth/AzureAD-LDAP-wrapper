# Pronto 4GL RAG Assistant

A local AI system for Pronto 4GL code analysis and editing, built with FastAPI, ChromaDB, and Ollama.

## Features

- Document upload and processing
- Code analysis and suggestions
- Code generation capabilities
- Web and terminal interfaces
- Local deployment

## Requirements

- Python 3.9+
- 16GB RAM
- 4GHz CPU
- 20GB Storage

## Installation

1. Install dependencies:
```bash
poetry install
```

2. Start the server:
```bash
poetry run uvicorn src.api.routes:app --reload
```

## Usage

Access the web interface at http://localhost:8000

### API Endpoints

- `POST /api/documents`: Upload Pronto 4GL documents
- `POST /api/analyze`: Analyze code
- `POST /api/generate`: Generate code
- `POST /api/train`: Train system with Pronto 4GL code
- `GET /health`: Check system status

### Training the System

1. Create a directory with your Pronto 4GL code files
2. Use the training script:
```bash
poetry run python scripts/train_system.py /path/to/code/directory
```

Or use the API endpoint:
```bash
curl -X POST http://localhost:8000/api/train -H "Content-Type: application/json" -d '{"directory": "/path/to/code/directory"}'
```

## Architecture

- FastAPI backend
- ChromaDB for vector storage
- Ollama for LLM
- React frontend
