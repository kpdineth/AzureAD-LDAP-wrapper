from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

app = FastAPI(title="Pronto 4GL Assistant")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str
    context_size: int = 3

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        # TODO: Implement document processing
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_system(query: Query):
    try:
        # TODO: Implement query processing
        return {"response": "Query received", "query": query.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
