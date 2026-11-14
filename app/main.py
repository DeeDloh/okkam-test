from fastapi import FastAPI, File, UploadFile, Depends, Form

from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as okkam_router

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(okkam_router, tags=["getPercent"])