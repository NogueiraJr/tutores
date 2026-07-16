from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from app.api import tutors, chat
from app.core.database import engine, Base

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tutores API", version="1.0.0")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # For demo only
)

# Routes
app.include_router(tutors.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Tutores API - DOT Digital Group Challenge"}

@app.get("/health")
def health():
    return {"status": "healthy"}
