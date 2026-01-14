# Todo RAG Chatbot

A production-ready, multi-user todo application with RAG-enhanced natural language interface, built with Cohere RAG, FastAPI, and Claude Code with Spec-Kit Plus. This application follows a strict spec-driven development methodology with no manual coding.

## Features

- ✅ Natural language task management via RAG-enhanced chat interface
- ✅ User registration and authentication with Better Auth
- ✅ Create tasks with title and description using natural language
- ✅ View task list (newest first) with natural language queries
- ✅ Mark tasks as complete/incomplete via chat commands
- ✅ Edit task details using conversational interface
- ✅ Delete tasks with confirmation via natural language
- ✅ Session persistence (7 days)
- ✅ Strict user isolation
- ✅ Context-aware responses using RAG technology
- ✅ MCP tool integration for all task operations
- ✅ Comprehensive error handling and logging
- ✅ Stateless server architecture for scalability

## Quick Start

See `specs/003-rag-todo-chatbot/quickstart.md` for detailed setup instructions.

### Prerequisites
- Python 3.11+
- Node.js 18+
- Neon PostgreSQL account
- Cohere API key
- Better Auth configuration

### Setup
1. Generate JWT secret: `openssl rand -base64 32`
2. Configure `.env` files with BETTER_AUTH_SECRET, DATABASE_URL, and COHERE_API_KEY
3. Run backend: `cd backend && pip install -r requirements.txt && uvicorn src.main:app --reload`
4. Run frontend: `cd frontend && npm install && npm run dev`
5. Visit: http://localhost:3000

## Production Deployment

### Backend (Hugging Face Space)
Deploy the backend to Hugging Face Spaces:
1. Create a Hugging Face Space with the backend code
2. Configure environment variables:
   - `BETTER_AUTH_SECRET`: Your JWT secret
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `COHERE_API_KEY`: Your Cohere API key for RAG functionality
3. The backend will be accessible at: `https://your-username-todo-phase02.hf.space`

### Frontend (Vercel)
Deploy the frontend on Vercel:
1. Push your code to a GitHub repository
2. Connect your repository to Vercel
3. In the Vercel dashboard, set the following environment variables:
   - `NEXT_PUBLIC_API_URL`: Your Hugging Face backend URL (e.g., `https://kashafaman123-todo-phase02.hf.space`)
   - `NEXT_PUBLIC_COHERE_DOMAIN_KEY`: Your Cohere domain key for frontend integration
   - `BETTER_AUTH_SECRET`: The same JWT secret used in your backend
4. Set the build command to: `cd frontend && npm install && npm run build`
5. Set the output directory to: `frontend/.next`

### Important Notes
- Both frontend and backend must use the same `BETTER_AUTH_SECRET`
- The backend is configured to allow CORS requests from `https://hackathon2-phase1-five.vercel.app`
- Make sure both services are deployed and running before testing
- Configure domain allowlist for Cohere RAG integration

## Project Governance

This project follows the Todo RAG Chatbot Constitution which mandates:
- Spec-driven development methodology with Claude Code and Spec-Kit Plus
- No manual coding - all implementation through AI agents
- MCP tool integration for all task operations
- RAG-enhanced functionality for context-aware responses
- Stateless server architecture for scalability

## Documentation
- Constitution: `.specify/memory/constitution.md`
- Specification: `specs/003-rag-todo-chatbot/spec.md`
- Implementation Plan: `specs/003-rag-todo-chatbot/plan.md`
- API Contract: `specs/003-rag-todo-chatbot/contracts/api-contract.md`
- Quickstart Guide: `specs/003-rag-todo-chatbot/quickstart.md`
- Task Lists: `specs/003-rag-todo-chatbot/tasks.md`
