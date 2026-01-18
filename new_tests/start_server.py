import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="backend/.env")

# Explicitly set the environment variables to ensure they're available before any imports
os.environ.setdefault("DATABASE_URL", "sqlite:///./todo_app.db")
os.environ.setdefault("BETTER_AUTH_SECRET", "supersecretkeyformyappthatisatleast32characterslong")
os.environ.setdefault("COHERE_API_KEY", "your-cohere-api-key-here")

# Add backend/src to the Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend', 'src'))

# Now import and run the application
import uvicorn
# Import the app directly using sys.path modification
from main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)