# Quickstart Guide: Phase II Full-Stack Todo Application

**Feature**: 001-fullstack-todo-app
**Date**: 2025-12-30
**Purpose**: Step-by-step guide for local development setup and first task flow

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.11 or higher**: Backend runtime
  - Verify: `python --version` or `python3 --version`
  - Install: https://www.python.org/downloads/

- **Node.js 18 or higher**: Frontend runtime
  - Verify: `node --version`
  - Install: https://nodejs.org/

- **npm or yarn**: Node package manager
  - Verify: `npm --version` or `yarn --version`
  - Comes with Node.js installation

- **Git**: Version control
  - Verify: `git --version`
  - Install: https://git-scm.com/downloads

- **Neon PostgreSQL Account**: Cloud database
  - Sign up: https://neon.tech/ (free tier available)
  - Create new project and obtain connection string

## 1. Clone Repository

```bash
git clone <repository-url>
cd Todo-app-ph2
git checkout 001-fullstack-todo-app
```

## 2. Environment Setup

### 2.1 Generate Shared Secret

Generate a cryptographically secure secret for JWT signing/verification:

```bash
# On Unix/Linux/Mac:
openssl rand -base64 32

# On Windows (PowerShell):
$bytes = New-Object byte[] 32
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

Copy the output - you'll need it in the next step.

### 2.2 Configure Environment Variables

Create root `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and set:

```env
# Shared JWT secret (use output from Step 2.1)
BETTER_AUTH_SECRET=<your-generated-secret-here>

# Neon PostgreSQL connection string
DATABASE_URL=postgresql://username:password@host/database?sslmode=require

# API Base URL (for frontend)
NEXT_PUBLIC_API_URL=http://localhost:7860
```

**Get Neon DATABASE_URL**:
1. Log in to https://console.neon.tech/
2. Select your project
3. Go to "Connection Details"
4. Copy connection string (format: `postgresql://user:pass@host/dbname?sslmode=require`)

### 2.3 Configure Backend Environment

```bash
cd backend
cp .env.example .env
```

Backend `.env` should contain:

```env
BETTER_AUTH_SECRET=<same-secret-as-root-.env>
DATABASE_URL=<same-neon-url-as-root-.env>
```

### 2.4 Configure Frontend Environment

```bash
cd frontend
cp .env.local.example .env.local
```

Frontend `.env.local` should contain:

```env
BETTER_AUTH_SECRET=<same-secret-as-root-.env>
NEXT_PUBLIC_API_URL=http://localhost:7860
```

**Critical**: All three files (root `.env`, `backend/.env`, `frontend/.env.local`) MUST use the same `BETTER_AUTH_SECRET` value.

## 3. Backend Setup

### 3.1 Install Python Dependencies

```bash
cd backend  # If not already in backend directory
python -m venv venv  # Create virtual environment

# Activate virtual environment:
# On Unix/Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 3.2 Initialize Database

Database tables created automatically on first backend startup via SQLModel's `create_all()` method. No manual migration required.

To verify database connection:

```bash
python -c "from src.database import engine; from src.models import Task, User; from sqlmodel import SQLModel; SQLModel.metadata.create_all(engine); print('Database initialized successfully')"
```

Expected output: `Database initialized successfully`

### 3.3 Start Backend Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Verify backend health:
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

**Keep this terminal running** - backend must stay active while using the application.

## 4. Frontend Setup

Open a **new terminal** (keep backend terminal running).

### 4.1 Install Node Dependencies

```bash
cd frontend  # From repository root
npm install
# or
yarn install
```

### 4.2 Start Frontend Development Server

```bash
npm run dev
# or
yarn dev
```

Expected output:
```
▲ Next.js 16.0.0
- Local:        http://localhost:3000
- Ready in 2.1s
```

Open browser to http://localhost:3000

## 5. First User Flow

### 5.1 User Registration (Signup)

1. Navigate to http://localhost:3000
2. Click "Sign Up" or go to http://localhost:3000/signup
3. Enter email: `test@example.com`
4. Enter password: `testpassword123` (minimum 8 characters)
5. Click "Sign Up"

**Expected Result**:
- Account created successfully
- Automatically signed in
- Redirected to task list page (`/tasks`)
- Empty task list displayed with "Create your first task" message

### 5.2 Create First Task

1. On task list page, click "Add Task" button
2. Enter title: `Buy groceries`
3. Enter description (optional): `Milk, eggs, bread`
4. Click "Save" or "Create"

**Expected Result**:
- Task appears in list immediately
- Task shows title, description, and incomplete status (unchecked checkbox)
- Task displays creation timestamp

### 5.3 Mark Task Complete

1. Click checkbox next to "Buy groceries" task

**Expected Result**:
- Task marked as complete (checked checkbox)
- Visual indication of completion (strikethrough text or different styling)
- Completion persists after page refresh

### 5.4 Create Additional Tasks

1. Click "Add Task"
2. Create task: `Call dentist` (no description)
3. Create task: `Finish project report` with description: `Include Q4 metrics`

**Expected Result**:
- Three total tasks in list
- Tasks ordered by creation time (newest first)
- Each task shows correct completion status

### 5.5 Edit Task

1. Click "Edit" button on "Finish project report" task
2. Update title to: `Finish Q4 project report`
3. Update description to: `Include Q4 metrics and recommendations`
4. Click "Save"

**Expected Result**:
- Task updated with new title and description
- Updated_at timestamp changes
- Task remains in list

### 5.6 Delete Task

1. Click "Delete" button on "Call dentist" task
2. Confirm deletion in confirmation dialog

**Expected Result**:
- Task permanently removed from list
- Two remaining tasks displayed
- Deleted task does not reappear after refresh

### 5.7 Sign Out and Sign In

1. Click "Sign Out" or "Logout" button
2. Redirected to login page
3. Enter email: `test@example.com`
4. Enter password: `testpassword123`
5. Click "Sign In"

**Expected Result**:
- Successfully authenticated
- Redirected to task list
- All previous tasks still present (data persisted)
- Completion status preserved

### 5.8 Test User Isolation (Multi-User)

1. Sign out from first account
2. Sign up with new account: `user2@example.com` / `password456`
3. View task list

**Expected Result**:
- Empty task list for new user
- First user's tasks NOT visible
- Create task for user2, verify it doesn't appear in user1's list (sign in as user1 to confirm)

## 6. API Testing (Optional)

### 6.1 Obtain JWT Token

Sign in via frontend, then extract JWT from browser developer tools:

1. Open browser DevTools (F12)
2. Go to Application/Storage → Cookies
3. Find cookie containing JWT token (name varies by Better Auth config)
4. Copy token value

Or extract from network request Authorization header.

### 6.2 Test API Endpoints with curl

Replace `<JWT_TOKEN>` with actual token from step 6.1:

**List tasks:**
```bash
curl -H "Authorization: Bearer <JWT_TOKEN>" \
     http://localhost:8000/api/<user_id>/tasks
```

**Create task:**
```bash
curl -X POST \
     -H "Authorization: Bearer <JWT_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"title":"API test task","description":"Created via curl"}' \
     http://localhost:8000/api/<user_id>/tasks
```

**Update task:**
```bash
curl -X PUT \
     -H "Authorization: Bearer <JWT_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"title":"Updated title","description":"Updated description"}' \
     http://localhost:8000/api/<user_id>/tasks/1
```

**Toggle completion:**
```bash
curl -X PATCH \
     -H "Authorization: Bearer <JWT_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"completed":true}' \
     http://localhost:8000/api/<user_id>/tasks/1/complete
```

**Delete task:**
```bash
curl -X DELETE \
     -H "Authorization: Bearer <JWT_TOKEN>" \
     http://localhost:8000/api/<user_id>/tasks/1
```

**Test unauthorized access (missing token):**
```bash
curl http://localhost:8000/api/<user_id>/tasks
# Expected: 401 Unauthorized
```

## 7. Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: Activate virtual environment and reinstall dependencies
  ```bash
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install -r requirements.txt
  ```

**Error**: `sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server failed`
- **Solution**: Verify Neon DATABASE_URL is correct and database is accessible
  - Check connection string format
  - Verify Neon project is active (not paused)
  - Test connection with: `psql <DATABASE_URL>`

**Error**: `KeyError: 'BETTER_AUTH_SECRET'`
- **Solution**: Ensure backend/.env file exists and contains BETTER_AUTH_SECRET variable

### Frontend won't start

**Error**: `Error: Cannot find module 'next'`
- **Solution**: Install dependencies
  ```bash
  cd frontend
  npm install
  ```

**Error**: `ReferenceError: NEXT_PUBLIC_API_URL is not defined`
- **Solution**: Create frontend/.env.local file with NEXT_PUBLIC_API_URL=http://localhost:8000

### Authentication issues

**Problem**: "Could not validate credentials" error when accessing tasks
- **Solution**: Verify BETTER_AUTH_SECRET is identical in all three .env files (root, backend, frontend)
- **Solution**: Check JWT token hasn't expired (default 7 days) - try signing in again

**Problem**: User can see other users' tasks
- **Solution**: CRITICAL SECURITY ISSUE - report immediately. Backend must filter tasks by user_id from JWT.

### Database issues

**Problem**: Tables not created
- **Solution**: Backend creates tables automatically on startup. Check backend logs for SQLModel errors.
- **Solution**: Run manual table creation:
  ```bash
  cd backend
  python -c "from src.database import engine; from sqlmodel import SQLModel; from src.models import Task, User; SQLModel.metadata.create_all(engine)"
  ```

**Problem**: "Task not found" error for valid task IDs
- **Solution**: Task may belong to different user. Verify user_id in JWT matches task owner.

### CORS errors

**Problem**: Frontend shows CORS policy error when calling backend API
- **Solution**: Verify backend CORS middleware allows frontend origin (http://localhost:3000)
- **Solution**: Check NEXT_PUBLIC_API_URL in frontend/.env.local matches backend URL

## 8. Next Steps

After completing quickstart:

1. **Review Implementation Plan**: Read `@specs/001-fullstack-todo-app/plan.md` for architecture details
2. **Understand Data Model**: Review `@specs/001-fullstack-todo-app/data-model.md` for database schema
3. **Explore API Contract**: See `@specs/001-fullstack-todo-app/contracts/api-spec.yaml` for endpoint specifications
4. **Run Tests**: Execute backend tests with `pytest` (after test implementation in later phases)
5. **Contribute Code**: Follow spec-driven workflow (spec → plan → tasks → implement → validate)

## 9. Development Workflow

For implementing new features or fixing bugs:

1. **Read Specification**: Check `@specs/001-fullstack-todo-app/spec.md` for requirements
2. **Update Plan**: Modify `plan.md` if architecture changes needed
3. **Generate Tasks**: Run `/sp.tasks` command to break work into steps
4. **Implement**: Code generation via Claude Code following tasks
5. **Test**: Verify acceptance criteria from spec
6. **Commit**: Use `/sp.git.commit_pr` skill to commit and create PR

## 10. Production Deployment

**Note**: Production deployment out of scope for Phase II. For future reference:

- Deploy backend to cloud provider (AWS, GCP, Azure, Heroku)
- Deploy frontend to Vercel, Netlify, or similar
- Use managed secrets (AWS Secrets Manager, Azure Key Vault)
- Configure production DATABASE_URL pointing to Neon production database
- Enable HTTPS for all endpoints
- Rotate BETTER_AUTH_SECRET periodically
- Implement rate limiting and monitoring

---

**Support**: For issues or questions, refer to:
- Project specification: `@specs/001-fullstack-todo-app/spec.md`
- Implementation plan: `@specs/001-fullstack-todo-app/plan.md`
- Constitution: `.specify/memory/constitution.md`
- Root CLAUDE.md: Development guidance and conventions

**Quickstart Status**: ✅ Complete - Ready for local development
