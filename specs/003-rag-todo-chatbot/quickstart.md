# Quickstart Guide: RAG Todo Chatbot

## Prerequisites
- Python 3.11+
- Node.js 18+
- Neon PostgreSQL account
- Cohere API key
- Better Auth configuration

## Setup Instructions

### 1. Clone and Navigate to Project
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Backend Setup
1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables in `.env`:
   ```
   DATABASE_URL=your_neon_postgresql_connection_string
   BETTER_AUTH_SECRET=your_jwt_secret
   COHERE_API_KEY=your_cohere_api_key
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the backend server:
   ```bash
   uvicorn src.main:app --reload
   ```

### 3. Frontend Setup
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables in `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend URL
   NEXT_PUBLIC_COHERE_DOMAIN_KEY=your_cohere_domain_key
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   ```

### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend API Docs: http://localhost:8000/docs

## Usage
1. Register or login to the application
2. Use natural language to interact with your todo list:
   - "Add a task to buy groceries"
   - "Show me my tasks"
   - "Mark task 3 as complete"
   - "Update the meeting task to tomorrow"
   - "Delete the old task"

## Troubleshooting
- If you encounter database connection issues, verify your Neon PostgreSQL connection string
- If authentication fails, check your Better Auth configuration
- If RAG features don't work, verify your Cohere API key and domain allowlist settings