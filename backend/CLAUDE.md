# Backend Implementation Guidance

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT verification using python-jose
- **ASGI Server**: Uvicorn

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel entities (User, Task)
│   ├── api/
│   │   ├── routes/      # API endpoints (tasks.py, health.py)
│   │   └── dependencies.py  # JWT verification
│   ├── database.py      # Neon PostgreSQL connection
│   ├── config.py        # Environment variables
│   └── main.py          # FastAPI app initialization
├── tests/               # Test files
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (gitignored)
```

## Key Principles

### 1. JWT Security (CRITICAL)

**User Identity Derivation**:
- ALWAYS derive user_id from JWT token payload, NEVER from request parameters or body
- JWT token verified on EVERY request via `get_current_user()` dependency
- Path parameter `{user_id}` is IGNORED for security - token payload is source of truth

**Example**:
```python
@router.get("/api/{user_id}/tasks")
async def list_tasks(
    current_user: User = Depends(get_current_user),  # JWT verification
    session: Session = Depends(get_session)
):
    # CORRECT: Use current_user.id from JWT
    tasks = session.query(Task).filter(Task.user_id == current_user.id).all()

    # WRONG: NEVER use path parameter for user_id
    # tasks = session.query(Task).filter(Task.user_id == user_id).all()
```

### 2. User Isolation (CRITICAL)

**Enforcement**:
- EVERY database query MUST filter by authenticated user's ID from JWT
- Verify task ownership before update/delete operations
- Return 403 Forbidden if user attempts to access another user's data

**Example**:
```python
# Get single task with ownership verification
task = session.query(Task).filter(
    Task.id == task_id,
    Task.user_id == current_user.id  # Ownership check
).first()

if not task:
    # Could be non-existent OR belongs to different user
    raise HTTPException(status_code=404, detail="Task not found")
```

### 3. Database Session Management

**Pattern**:
```python
def get_session():
    with Session(engine) as session:
        yield session
        # Automatic commit/rollback handled by FastAPI
```

### 4. Request/Response Models

**Separation of Concerns**:
- **Request Models** (Pydantic): `TaskCreate`, `TaskUpdate`, `TaskCompletionToggle`
- **Response Models** (Pydantic): `TaskResponse` with explicit fields
- **Database Models** (SQLModel): `Task` with table=True

**Never expose internal fields** in API responses (e.g., never return `password_hash`).

### 5. Error Handling

**Standard Error Responses**:
```python
# 401 Unauthorized - Invalid/missing JWT
raise HTTPException(status_code=401, detail="Could not validate credentials")

# 403 Forbidden - Valid token but no permission
raise HTTPException(status_code=403, detail="Access denied: user ID mismatch")

# 404 Not Found - Resource doesn't exist
raise HTTPException(status_code=404, detail="Task not found")

# 400 Bad Request - Validation failure
# (Automatically handled by Pydantic models)
```

### 6. CORS Configuration

**Development Setup**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Implementation Checklist

### Database Layer
- [ ] SQLModel entities with proper relationships and indexes
- [ ] Foreign key constraints (task.user_id → user.id)
- [ ] Automatic timestamp updates (updated_at)
- [ ] Connection pooling configured

### Authentication
- [ ] JWT signature verification using BETTER_AUTH_SECRET
- [ ] Token expiration validation
- [ ] User_id extraction from payload
- [ ] 401 error handling for invalid tokens

### API Endpoints
- [ ] All endpoints require JWT authentication
- [ ] User isolation enforced on ALL queries
- [ ] Ownership verification before modify operations
- [ ] Proper HTTP status codes (200, 201, 204, 400, 401, 403, 404)

### Validation
- [ ] Title: Required, 1-255 characters
- [ ] Description: Optional, max 2000 characters
- [ ] Completion status: Boolean only
- [ ] Timestamps: Auto-managed

## Common Pitfalls to Avoid

1. ❌ Using path parameter `user_id` instead of JWT token
2. ❌ Forgetting user isolation filter on queries
3. ❌ Not verifying task ownership before updates
4. ❌ Exposing sensitive fields in API responses
5. ❌ Hardcoding secrets instead of using environment variables
6. ❌ Missing CORS configuration (frontend can't call backend)
7. ❌ Not handling database session lifecycle properly

## Running the Backend

### Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Health Check
```bash
curl http://localhost:7860/health
# Expected: {"status": "healthy"}
```

## Reference Documents

- Specification: `@specs/001-fullstack-todo-app/spec.md`
- Implementation Plan: `@specs/001-fullstack-todo-app/plan.md`
- Data Model: `@specs/001-fullstack-todo-app/data-model.md`
- API Contract: `@specs/001-fullstack-todo-app/contracts/api-spec.yaml`
- Research Decisions: `@specs/001-fullstack-todo-app/research.md`
