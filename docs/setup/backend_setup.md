# Backend Setup Instructions

## Prerequisites
- Python 3.9+
- Poetry
- Ollama
- 16GB RAM minimum
- 20GB storage

## Installation Steps

1. Clone the repository:
```bash
git clone [repository-url]
cd pronto-rag-assistant
```

2. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Install and configure Ollama:
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull required model
ollama pull llama2
```

5. Configure environment:
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
```

6. Start the server:
```bash
poetry run uvicorn src.api.routes:app --reload
```

## Development Setup

### Virtual Environment
```bash
# Create and activate virtual environment
poetry shell

# Verify Python version
python --version  # Should be 3.9+
```

### Database Setup
```bash
# Create data directory
mkdir -p data/chroma

# Set permissions
chmod 755 data/chroma
```

### Project Structure
```
src/
├── api/          # FastAPI routes
├── core/         # Core functionality
├── training/     # Training system
└── cli/          # Command-line interface
```

## Configuration

### Environment Variables
```env
# LLM Configuration
OLLAMA_MODEL=llama2
OLLAMA_CONTEXT_WINDOW=4096
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=512

# Database Configuration
CHROMA_PERSIST_DIRECTORY=data/chroma
CHROMA_COLLECTION_NAME=pronto4gl_code

# API Configuration
API_HOST=localhost
API_PORT=8000
API_WORKERS=4

# Security
API_KEY=your_api_key_here
```

## Testing

1. Run tests:
```bash
poetry run pytest
```

2. Test API endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Analyze code
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "FUNCTION example()\n    RETURN TRUE\nEND FUNCTION"}'
```

## Troubleshooting

### Common Issues

1. Port already in use:
```bash
# Find process using port 8000
sudo lsof -i :8000
sudo kill -9 [PID]
```

2. Ollama issues:
```bash
# Restart Ollama
sudo systemctl restart ollama

# Check Ollama status
curl http://localhost:11434/api/tags
```

3. Database issues:
```bash
# Clear database
rm -rf data/chroma/*

# Recreate directory
mkdir -p data/chroma
```

## Production Deployment

1. Configure production settings:
```bash
# Edit .env
API_HOST=0.0.0.0
API_WORKERS=4
```

2. Start production server:
```bash
poetry run uvicorn src.api.routes:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

## Security Considerations

1. API Security:
   - Use API keys
   - Enable CORS protection
   - Rate limiting
   - Input validation

2. File Security:
   - Size limits
   - Type validation
   - Content scanning

3. Database Security:
   - Access control
   - Data encryption
   - Regular backups

## Performance Optimization

1. Server Configuration:
   - Adjust worker count
   - Configure timeouts
   - Enable compression

2. Database Optimization:
   - Index management
   - Query optimization
   - Caching strategies

## Monitoring

1. System Monitoring:
   - CPU usage
   - Memory usage
   - Disk space
   - Network traffic

2. Application Monitoring:
   - Request latency
   - Error rates
   - API usage
   - Model performance

## Maintenance

1. Regular Tasks:
   - Update dependencies
   - Backup data
   - Log rotation
   - Model updates

2. Health Checks:
   - API endpoints
   - Database connection
   - LLM availability
   - Storage capacity
