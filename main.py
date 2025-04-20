# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from analyze.consistency import router as consistency_router
from fastapi.responses import JSONResponse

app = FastAPI(
    title="RAG Analyzer API",
    description="API for analyzing documents using RAG (Retrieval Augmented Generation)",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "Welcome to RAG Analyzer API",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }
    )

# Mount routes
app.include_router(consistency_router, prefix="/api/v1")
