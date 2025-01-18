# In-Memory Database Setup Guide

## Overview
The Pronto 4GL Assistant uses ChromaDB as its vector database for storing and retrieving code embeddings. This guide explains how to set up and configure the in-memory database system.

## Installation

1. Install dependencies using Poetry:
```bash
poetry install
```

This will install ChromaDB and all required dependencies from pyproject.toml.

## Configuration

### Basic Setup
```python
from src.core.database import DatabaseManager

# In-memory storage (data is lost when process ends)
db = DatabaseManager()

# Persistent storage (data is saved to disk)
db = DatabaseManager(persist_directory="data/chroma")
```

### Memory Management
- Recommended RAM: 16GB minimum
- Storage requirements: 
  - In-memory: ~2GB base + data size
  - Persistent: ~1GB + data size
- Maximum document size: 1GB per document

### Configuration Options
```python
# ChromaDB settings
settings = Settings(
    allow_reset=True,
    anonymized_telemetry=False
)

# Collections configuration
code_collection = client.get_or_create_collection(
    name="pronto4gl_code",
    metadata={"hnsw:space": "cosine"}
)
```

## Usage Examples

### Adding Documents
```python
# Add a code snippet
doc_id = db.add_code_snippet(
    code="FUNCTION example()\n    RETURN TRUE\nEND FUNCTION",
    metadata={"type": "function", "language": "pronto4gl"},
    embedding=[0.1, 0.2, 0.3]  # Vector representation
)

# Add a document
doc_id = db.add_document(
    content="Document content...",
    metadata={"filename": "example.4gl"},
    embedding=[0.1, 0.2, 0.3]
)
```

### Querying Similar Code
```python
# Find similar code snippets
results = db.query_similar_code(
    query_embedding=[0.1, 0.2, 0.3],
    n_results=3
)

# Find similar documents
results = db.query_similar_documents(
    query_embedding=[0.1, 0.2, 0.3],
    n_results=3
)
```

### Retrieving Documents
```python
# Get code by ID
code = db.get_code_by_id("code_123")

# Get document by ID
document = db.get_document_by_id("doc_123")
```

## Performance Optimization

### Memory Usage
1. Use persistent storage for large datasets
2. Implement batch processing for large operations
3. Monitor memory usage with logging

### Query Optimization
1. Use appropriate embedding dimension (384 default)
2. Optimize chunk sizes for your use case
3. Use metadata filtering when possible

## Troubleshooting

### Common Issues

1. Memory Errors
```
Solution: Enable persistent storage or reduce batch sizes
```

2. Slow Queries
```
Solution: 
- Optimize chunk sizes
- Use metadata filtering
- Consider index optimization
```

3. Data Persistence Issues
```
Solution:
- Verify write permissions
- Check disk space
- Use absolute paths
```

### Logging
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Maintenance

### Regular Tasks
1. Optimize indexes periodically
2. Monitor disk usage for persistent storage
3. Clean up old data as needed

### Backup Strategy
1. Regular backups of persistent directory
2. Version control for configuration
3. Document backup schedule

## Security Considerations

1. Access Control
- Use API keys for authentication
- Implement role-based access
- Secure persistent storage directory

2. Data Protection
- Encrypt sensitive data
- Sanitize inputs
- Regular security audits

## System Requirements

### Minimum Requirements
- Python 3.9+
- RAM: 16GB
- Storage: 20GB
- CPU: 4 cores

### Recommended Requirements
- Python 3.11+
- RAM: 32GB
- Storage: 50GB
- CPU: 8 cores
- SSD storage for persistence

## Monitoring

### Key Metrics
1. Memory usage
2. Query latency
3. Storage utilization
4. Error rates

### Logging Configuration
```python
# Configure logging
logging.config.dictConfig({
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'database.log',
            'level': 'DEBUG'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
})
```

## Development Setup

### Local Development
1. Clone repository
2. Install dependencies
3. Configure environment
4. Initialize database

### Testing
```bash
# Run database tests
poetry run pytest tests/core/test_database.py
```

## Upgrading

### Version Compatibility
- ChromaDB: ^0.6.3
- sentence-transformers: ^2.2.2
- Python: ^3.9

### Upgrade Steps
1. Backup data
2. Update dependencies
3. Migrate data if needed
4. Test functionality

## Support

### Getting Help
- Check logs for detailed errors
- Review documentation
- Submit issues with details
- Contact maintainers

### Contributing
- Follow coding standards
- Add tests for new features
- Update documentation
- Submit pull requests
