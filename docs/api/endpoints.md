# API Endpoints Documentation

## Overview
The Pronto 4GL Assistant API provides endpoints for document processing, code analysis, code generation, and system training. All endpoints return JSON responses and handle errors consistently.

## Base URL
```
http://localhost:8000/api
```

## Authentication
Authentication is handled via API key in headers:
```http
Authorization: Bearer ${API_KEY}
```

## Endpoints

### 1. Document Upload
**Endpoint**: `POST /documents`
**Purpose**: Upload and process Pronto 4GL documents

**Request**:
```http
POST /api/documents
Content-Type: multipart/form-data

file: <file>
```

**Specifications**:
- Maximum file size: 1GB
- Supported formats: .4gl, .txt, .md
- Content validation enforced

**Response**:
```json
{
  "status": "success",
  "filename": "example.4gl",
  "metadata": {
    "size": 1024,
    "type": "4gl",
    "timestamp": "2024-01-18T12:00:00Z"
  },
  "suggestions": [
    {
      "type": "style",
      "line": 10,
      "message": "Consider adding documentation"
    }
  ]
}
```

**Error Responses**:
```json
{
  "status": "error",
  "detail": "File too large (max: 1GB)"
}
```

### 2. Code Analysis
**Endpoint**: `POST /analyze`
**Purpose**: Analyze Pronto 4GL code snippets

**Request**:
```http
POST /api/analyze
Content-Type: application/json

{
  "code": "FUNCTION get_customer_details(customer_code)\n    SELECT * FROM customers\n    WHERE code = :customer_code\nEND FUNCTION"
}
```

**Response**:
```json
{
  "status": "success",
  "analysis": {
    "quality_score": 8.5,
    "suggestions": [
      {
        "type": "security",
        "line": 2,
        "message": "Consider parameterizing SQL query"
      }
    ],
    "similar_patterns": [
      {
        "code": "...",
        "similarity": 0.85
      }
    ]
  }
}
```

### 3. Code Generation
**Endpoint**: `POST /generate`
**Purpose**: Generate Pronto 4GL code from descriptions

**Request**:
```http
POST /api/generate
Content-Type: application/json

{
  "description": "Create a function to validate customer credit limit",
  "context": {
    "database_schema": "customers",
    "required_fields": ["credit_limit", "balance"]
  }
}
```

**Response**:
```json
{
  "status": "success",
  "generated_code": {
    "code": "FUNCTION validate_credit_limit(customer_id)\n    ...",
    "explanation": "This function checks the customer's current balance...",
    "usage_example": "CALL validate_credit_limit('CUST001')"
  }
}
```

### 4. Training System
**Endpoint**: `POST /train`
**Purpose**: Train system with Pronto 4GL code examples

**Request**:
```http
POST /api/train
Content-Type: application/json

{
  "directory": "/path/to/code",
  "options": {
    "recursive": true,
    "file_types": [".4gl"]
  }
}
```

**Response**:
```json
{
  "status": "success",
  "training_results": {
    "files_processed": 42,
    "patterns_learned": 156,
    "duration_seconds": 45,
    "model_version": "1.2.3"
  }
}
```

## Error Handling

### Standard Error Response
```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Human readable error message",
  "details": {
    "field": "Additional error context"
  }
}
```

### Common Error Codes
- `FILE_TOO_LARGE`: File exceeds 1GB limit
- `INVALID_FORMAT`: Unsupported file format
- `PARSE_ERROR`: Unable to parse code
- `TRAINING_ERROR`: Error during training process
- `GENERATION_ERROR`: Unable to generate code
- `VALIDATION_ERROR`: Input validation failed

## Rate Limiting
- 100 requests per minute per API key
- Rate limit headers included in responses:
  ```http
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1516131940
  ```

## Performance Requirements
Based on hardware specifications (16GB RAM, 4.00GHz CPU, no GPU):
- Document upload processing: < 5 seconds
- Code analysis: < 3 seconds
- Code generation: < 10 seconds
- Training: Variable based on dataset size

## Implementation Notes
The API is designed to work with the following backend components:
- DocumentProcessor: Handles file processing and validation
- CodeEmbeddings: Manages code vector embeddings
- LLMInterface: Interfaces with language model
- TrainingSystem: Manages system training

Each endpoint integrates with these components to provide its functionality while maintaining performance requirements within the specified hardware constraints.
