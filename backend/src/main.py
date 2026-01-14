from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.chat_api import router as chat_router
from .api.routes.tasks import router as tasks_router
from .api.routes.auth import router as auth_router
from .api.routes.health import router as health_router
import os
from dotenv import load_dotenv
from .logging_config import setup_error_handlers
from .security_config import setup_security


# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="RAG Todo Chatbot API",
    description="API for the RAG-enhanced Todo Chatbot with natural language interface",
    version="1.0.0"
)

# Add CORS middleware FIRST, before any other middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8000").split(",")
# Ensure we include the frontend URL that's making the request
default_origins = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"]
all_origins = list(set(allowed_origins + default_origins))  # Combine and deduplicate

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup security measures
setup_security(app)

# Setup error handlers
setup_error_handlers(app)

# Include routers
app.include_router(chat_router)
app.include_router(tasks_router)
app.include_router(auth_router)
# Note: health_router is not included since we have a health endpoint in main.py

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG Todo Chatbot API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "RAG Todo Chatbot API"}