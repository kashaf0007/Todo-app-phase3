import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend', 'src'))

# Test imports
try:
    from backend.src.api.chat_api import router
    print("[OK] Chat API router imported successfully")
except Exception as e:
    print(f"[ERROR] Chat API router import error: {e}")
    import traceback
    traceback.print_exc()

try:
    from backend.src.services.rag_service import RAGService
    print("[OK] RAG Service imported successfully")
except Exception as e:
    print(f"[ERROR] RAG Service import error: {e}")
    import traceback
    traceback.print_exc()

try:
    from backend.src.mcp.tools import MCPTaskTools
    print("[OK] MCP Task Tools imported successfully")
except Exception as e:
    print(f"[ERROR] MCP Task Tools import error: {e}")
    import traceback
    traceback.print_exc()

# Test initializing RAG service
try:
    from dotenv import load_dotenv
    load_dotenv()
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if cohere_api_key:
        rag_service = RAGService(cohere_api_key)
        print("[OK] RAG Service initialized successfully")
    else:
        print("[INFO] COHERE_API_KEY not found, skipping RAG initialization")
except Exception as e:
    print(f"[ERROR] RAG Service initialization error: {e}")
    import traceback
    traceback.print_exc()

# Test MCP tools
try:
    tools = MCPTaskTools()
    print("[OK] MCP Task Tools initialized successfully")
except Exception as e:
    print(f"[ERROR] MCP Task Tools initialization error: {e}")
    import traceback
    traceback.print_exc()