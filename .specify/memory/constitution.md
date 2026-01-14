<!-- SYNC IMPACT REPORT:
Version change: N/A (initial creation) → 1.0.0
Added sections: All sections (new constitution)
Removed sections: None
Templates requiring updates: N/A
Follow-up TODOs: None
-->
# Todo RAG Chatbot Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)
Every feature and change begins with a specification; Specifications must be complete and reviewed before implementation; No manual coding allowed - all implementation must be done through Claude Code with Spec-Kit Plus.

### II. Full-Stack Architecture
Complete web application with Cohere-powered RAG chat UI frontend and Python FastAPI backend; Natural language interface for all todo features with RAG integration for contextual recall; Stateless server design with conversation and task storage in Neon PostgreSQL.

### III. MCP Tool Integration
Chatbot must invoke MCP tools for all task operations (add_task, list_tasks, complete_task, delete_task, update_task); All tools return standardized responses with task_id, status, and title; Agent detects natural language cues to determine appropriate tool invocation.

### IV. RAG-Enhanced Functionality
Conversational interface enhanced with Retrieval-Augmented Generation for contextual task management; RAG retrieval queries historical tasks and context to provide intelligent suggestions; Context-aware responses based on conversation history and stored tasks.

### V. State Management
Stateless server architecture for scalability and resilience; Conversation history and tasks stored in Neon PostgreSQL database; Conversations resume correctly after server restart with preserved context.

### VI. User Experience
Friendly confirmation responses for all task actions; Graceful error handling for missing tasks or invalid requests; Natural language processing for intuitive task management.

## Technical Constraints

### Backend Requirements
Python FastAPI server with SQLModel ORM and Neon PostgreSQL database; Better Auth for authentication; MCP server integration for tool orchestration; RAG integration using Cohere technology.

### Frontend Requirements
Cohere Chat UI with RAG support for natural language interaction; Responsive design for task management interface; Proper domain allowlist configuration for production deployment.

### Data Management
Database tables required: tasks, conversations, messages; Proper migration scripts for schema changes; Conversation flow maintains context between user and assistant exchanges.

## Development Workflow

### Strict Spec-Driven Process
1. Write comprehensive specification using Spec-Kit Plus
2. Review and refine specification with stakeholders
3. Generate detailed development plan from specification
4. Break plan into testable implementation tasks
5. Implement exclusively through Claude Code - manual coding prohibited

### Quality Assurance
All implementations must pass reproducibility and testability requirements; Clean code practices with proper separation of concerns; Comprehensive error handling and validation at all levels.

## Deliverables

### Core Components
- `/frontend` - Cohere RAG Chat UI for natural language task management
- `/backend` - FastAPI + MCP + RAG logic for task processing
- `/specs` - Complete specification files following Spec-Kit Plus methodology
- Database migration scripts for Neon PostgreSQL schema management

### Functional Requirements
- Manage todos via natural language commands
- Provide context-aware suggestions using RAG
- Maintain stateless, scalable architecture
- Confirm all user actions with friendly responses
- Handle errors gracefully with informative messages

## Governance

This constitution governs all design, development, and evaluation decisions for the Todo RAG Chatbot project. All team members must adhere to the spec-driven workflow and MCP tool integration requirements. Any amendments to this constitution must follow the formal change management process with proper documentation and approval.

**Version**: 1.0.0 | **Ratified**: 2026-01-10 | **Last Amended**: 2026-01-10