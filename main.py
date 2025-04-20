# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from analyze.consistency import router as consistency_router
from app.api.analyze.route import router as analyze_router
from app.api.embed.route import router as embed_router
from app.api.analyze.sasb.draft.route import router as sasb_draft_router
from app.api.analyze.tcfd.improve.route import router as tcfd_improve_router
from app.api.analyze.tcfd.draft.route import router as tcfd_draft_router
from app.api.analyze.tcfd.analyze.route import router as tcfd_analyze_router
from app.api.analyze.tcfd.analyze.consistency.route import router as tcfd_consistency_router
from app.api.analyze.tcfd.analyze.consistency.consistency import router as tcfd_consistency_detail_router
from app.api.analyze.tcfd.analyze.consistency.consistency.consistency import router as tcfd_consistency_final_router
from app.api.analyze.tcfd.analyze.consistency.consistency.consistency.consistency import router as tcfd_consistency_complete_router

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

# Import and mount other routes
from app.api.analyze.route import router as analyze_router
from app.api.embed.route import router as embed_router
from app.api.convert_to_pdf.route import router as pdf_router
from app.api.score_insights.route import router as insights_router

app.include_router(analyze_router, prefix="/api")
app.include_router(embed_router, prefix="/api")
app.include_router(pdf_router, prefix="/api")
app.include_router(insights_router, prefix="/api")

# Additional routes
app.include_router(sasb_draft_router, prefix="/api")
app.include_router(tcfd_improve_router, prefix="/api")
app.include_router(tcfd_draft_router, prefix="/api")
app.include_router(tcfd_analyze_router, prefix="/api")
app.include_router(tcfd_consistency_router, prefix="/api")
app.include_router(tcfd_consistency_detail_router, prefix="/api")
app.include_router(tcfd_consistency_final_router, prefix="/api")
app.include_router(tcfd_consistency_complete_router, prefix="/api")
