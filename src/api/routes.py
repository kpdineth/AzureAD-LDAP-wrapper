"""Main FastAPI application for Pronto 4GL Assistant."""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
import os

from ..core.database import DatabaseManager
from ..core.document_processor import Pronto4GLProcessor
from ..core.embeddings import CodeEmbeddings
from ..core.llm import LLMInterface

# Initialize FastAPI app
app = FastAPI(title="Pronto 4GL Assistant")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = DatabaseManager()
processor = Pronto4GLProcessor()
embeddings = CodeEmbeddings()
llm = LLMInterface()

class CodeQuery(BaseModel):
    """Model for code analysis requests."""
    code: str
    context: Optional[Dict] = None

class GenerateRequest(BaseModel):
    """Model for code generation requests."""
    description: str
    context: Optional[Dict] = None

class TrainRequest(BaseModel):
    """Model for training requests."""
    directory: str
    options: Optional[Dict] = None

@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a Pronto 4GL document."""
    try:
        # Validate file type
        if not processor.validate_file(file.filename):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Read file content
        content = await file.read()
        
        # Check file size (1GB limit)
        if len(content) > 1024 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max: 1GB)")
        
        # Process document
        doc_content = content.decode("utf-8")
        processed = processor.process_document(doc_content)
        
        # Generate embeddings for chunks
        chunk_embeddings = embeddings.encode_code(processed["chunks"])
        
        # Store in database
        doc_ids = []
        for chunk, embedding in zip(processed["chunks"], chunk_embeddings):
            doc_id = db.add_document(
                content=chunk,
                metadata={
                    "filename": file.filename,
                    **processed["metadata"]
                },
                embedding=embedding
            )
            doc_ids.append(doc_id)
        
        return {
            "status": "success",
            "data": {
                "filename": file.filename,
                "metadata": processed["metadata"],
                "suggestions": processed["suggestions"],
                "doc_ids": doc_ids
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_code(query: CodeQuery):
    """Analyze Pronto 4GL code and provide suggestions."""
    try:
        print(f"Received code analysis request: {query.code}")  # Debug log
        
        # Generate embedding for query code
        print("Generating code embedding...")  # Debug log
        code_embedding = embeddings.encode_code([query.code])[0]
        
        # Find similar code examples
        print("Finding similar code examples...")  # Debug log
        similar_code = db.query_similar_code(code_embedding)
        print(f"Found {len(similar_code)} similar examples")  # Debug log
        
        # Generate analysis using LLM
        print("Generating code analysis...")  # Debug log
        analysis = llm.analyze_code(
            code=query.code,
            similar_examples=similar_code,
            context=query.context
        )
        print(f"Analysis completed: {analysis}")  # Debug log
        
        return {
            "status": "success",
            "data": {
                "analysis": analysis,
                "similar_code": similar_code[:3]  # Top 3 similar examples
            }
        }
    except Exception as e:
        print(f"Error in analyze_code: {str(e)}")  # Debug log
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_code(request: GenerateRequest):
    """Generate Pronto 4GL code from description."""
    try:
        # Generate embedding for description
        query_embedding = embeddings.encode_query(request.description)
        
        # Find similar code for context
        similar_code = db.query_similar_code(query_embedding)
        
        # Generate code using LLM
        generated = llm.generate_code(
            description=request.description,
            similar_examples=similar_code,
            context=request.context
        )
        
        return {
            "status": "success",
            "data": {
                "generated_code": generated["code"],
                "explanation": generated.get("explanation"),
                "similar_examples": similar_code[:3]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/train")
async def train_system(request: TrainRequest):
    """Train the system with Pronto 4GL code examples."""
    try:
        if not os.path.exists(request.directory):
            raise HTTPException(status_code=400, detail="Directory not found")
        
        # Initialize trainer
        from ..training import Pronto4GLTrainer
        trainer = Pronto4GLTrainer()
        
        # Train system
        result = trainer.train(request.directory)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        return {
            "status": "success",
            "data": {
                "documents_processed": result["documents_processed"],
                "chunks_created": result["chunks_created"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check system health."""
    return {"status": "healthy"}
