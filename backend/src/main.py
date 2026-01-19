from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .api.chat_api import router as chat_router
from .api.routes.tasks import router as tasks_router
from .api.routes.auth import router as auth_router
from .api.routes.health import router as health_router
from .config import get_settings
from .logging_config import setup_error_handlers
from .security_config import setup_security
from .auth import auth


# Load settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="RAG Todo Chatbot API",
    description="API for the RAG-enhanced Todo Chatbot with natural language interface",
    version="1.0.0"
)

# Add CORS middleware FIRST, before any other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_methods_list,
    allow_headers=settings.cors_headers_list,
)

# Setup security measures
setup_security(app)

# Setup error handlers
setup_error_handlers(app)

# Mount the .well-known directory to serve static files
import os

# Look for .well-known directory in multiple possible locations
well_known_path = None

# First, try the current working directory
project_root = os.getcwd()
well_known_path_candidate = os.path.join(project_root, ".well-known")
if os.path.exists(well_known_path_candidate):
    well_known_path = well_known_path_candidate

# If not found in cwd, try relative to the main.py file location (go up 3 levels to project root)
if well_known_path is None:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    well_known_path_candidate = os.path.join(project_root, ".well-known")
    if os.path.exists(well_known_path_candidate):
        well_known_path = well_known_path_candidate

# If still not found, try one level up from current working directory (for Docker container scenario)
if well_known_path is None:
    project_root = os.path.dirname(os.getcwd())
    well_known_path_candidate = os.path.join(project_root, ".well-known")
    if os.path.exists(well_known_path_candidate):
        well_known_path = well_known_path_candidate

# Only mount if the directory exists
if well_known_path:
    app.mount("/.well-known", StaticFiles(directory=well_known_path), name="well-known")
else:
    print("Warning: .well-known directory not found in any expected location. Skipping mount.")

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