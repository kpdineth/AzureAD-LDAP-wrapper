from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
import os

from ..core.document_processor import Pronto4GLProcessor
from ..core.embeddings import CodeEmbeddings
from ..core.llm import LLMInterface
from ..training import Pronto4GLTrainer

app = FastAPI(title="Pronto 4GL Assistant")

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
processor = Pronto4GLProcessor()
embeddings = CodeEmbeddings()
llm = LLMInterface()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class CodeQuery(BaseModel):
    code: str
    description: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def get_upload_page():
    """Return the HTML upload page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pronto 4GL Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .form-group { margin-bottom: 20px; }
            .btn { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            .results { margin-top: 20px; padding: 20px; background: #f8f9fa; }
            textarea { width: 100%; height: 200px; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Pronto 4GL Assistant</h1>
            
            <div class="form-group">
                <h2>Upload Document</h2>
                <form action="/api/documents" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".4gl,.txt,.md">
                    <button type="submit" class="btn">Upload</button>
                </form>
            </div>

            <div class="form-group">
                <h2>Analyze Code</h2>
                <textarea id="code" placeholder="Enter Pronto 4GL code here..."></textarea>
                <button onclick="analyzeCode()" class="btn">Analyze</button>
            </div>

            <div class="form-group">
                <h2>Generate Code</h2>
                <textarea id="description" placeholder="Describe what you want the code to do..."></textarea>
                <button onclick="generateCode()" class="btn">Generate</button>
            </div>

            <div class="form-group">
                <h2>Train System</h2>
                <input type="text" id="trainDirectory" placeholder="Enter path to code directory..." style="width: 100%; padding: 10px; margin-bottom: 10px;">
                <button onclick="trainSystem()" class="btn">Train</button>
            </div>

            <div id="results" class="results"></div>

            <script>
            async function analyzeCode() {
                const code = document.getElementById('code').value;
                try {
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({code})
                    });
                    const data = await response.json();
                    displayResults(data);
                } catch (error) {
                    console.error('Error:', error);
                    displayResults({error: 'Analysis failed: ' + error.message});
                }
            }

            async function generateCode() {
                const description = document.getElementById('description').value;
                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({description})
                    });
                    const data = await response.json();
                    displayResults(data);
                } catch (error) {
                    console.error('Error:', error);
                    displayResults({error: 'Code generation failed: ' + error.message});
                }
            }

            async function trainSystem() {
                const directory = document.getElementById('trainDirectory').value;
                if (!directory) {
                    displayResults({error: 'Please enter a directory path'});
                    return;
                }
                try {
                    const response = await fetch('/api/train', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({directory})
                    });
                    const data = await response.json();
                    displayResults(data);
                } catch (error) {
                    console.error('Error:', error);
                    displayResults({error: 'Training failed: ' + error.message});
                }
            }

            function displayResults(data) {
                const results = document.getElementById('results');
                results.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                if (data.error) {
                    results.classList.add('error');
                } else {
                    results.classList.remove('error');
                }
            }
        </div>

        <script>
        async function analyzeCode() {
            const code = document.getElementById('code').value;
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code})
                });
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function generateCode() {
            const description = document.getElementById('description').value;
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({description})
                });
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function displayResults(data) {
            const results = document.getElementById('results');
            results.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
        </script>
    </body>
    </html>
    """

@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a Pronto 4GL document."""
    try:
        if not processor.validate_file(file.filename):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        content = await file.read()
        if len(content) > 1024 * 1024 * 1024:  # 1GB limit
            raise HTTPException(status_code=400, detail="File too large (max: 1GB)")
        
        # Process document
        doc_content = content.decode("utf-8")
        processed_doc = processor.process_document(doc_content)
        
        # Generate embeddings
        doc_embeddings = embeddings.encode_code(processed_doc["chunks"])
        
        return {
            "status": "success",
            "filename": file.filename,
            "metadata": processed_doc["metadata"],
            "suggestions": processed_doc.get("suggestions", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_code(query: CodeQuery):
    """Analyze Pronto 4GL code and suggest improvements."""
    try:
        analysis = llm.analyze_code(query.code)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GenerateRequest(BaseModel):
    description: str

@app.post("/api/generate")
async def generate_code(request: GenerateRequest):
    """Generate Pronto 4GL code based on description."""
    try:
        if not request.description:
            raise HTTPException(status_code=400, detail="Description is required")
        
        # Log the request for debugging
        print(f"Generating code for description: {request.description}")
        
        # Generate code using LLM
        generated = llm.generate_code(request.description)
        
        # Log the response
        print(f"Generated response: {generated}")
        
        return generated
    except Exception as e:
        print(f"Error in generate_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class TrainingRequest(BaseModel):
    directory: str

@app.post("/api/train")
async def train_system(request: TrainingRequest):
    """Train the system with Pronto 4GL code from specified directory."""
    try:
        if not os.path.exists(request.directory):
            raise HTTPException(status_code=400, detail="Directory not found")
            
        trainer = Pronto4GLTrainer()
        result = trainer.train(request.directory)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check system health."""
    return {"status": "healthy"}
