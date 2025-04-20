# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from analyze.consistency import router as consistency_router  # Adjust path if needed

app = FastAPI()

# Enable CORS so frontend can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to ["http://localhost:3000"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(consistency_router)
