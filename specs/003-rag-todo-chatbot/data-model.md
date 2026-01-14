# Data Model: RAG Todo Chatbot

## Entity: Task
- **Fields**:
  - id (Integer, Primary Key, Auto-increment)
  - user_id (String, Foreign Key to User)
  - title (String, Required, Max 255 chars)
  - description (Text, Optional)
  - completed (Boolean, Default: False)
  - created_at (DateTime, Auto-generated)
  - updated_at (DateTime, Auto-generated)

- **Validation**:
  - Title must not be empty
  - User must exist

- **Relationships**:
  - Belongs to one User
  - User has many Tasks

## Entity: Conversation
- **Fields**:
  - id (Integer, Primary Key, Auto-increment)
  - user_id (String, Foreign Key to User)
  - created_at (DateTime, Auto-generated)
  - updated_at (DateTime, Auto-generated)

- **Validation**:
  - User must exist

- **Relationships**:
  - Belongs to one User
  - User has many Conversations
  - Has many Messages

## Entity: Message
- **Fields**:
  - id (Integer, Primary Key, Auto-increment)
  - user_id (String, Foreign Key to User)
  - conversation_id (Integer, Foreign Key to Conversation)
  - role (String, Required, Values: "user", "assistant")
  - content (Text, Required)
  - created_at (DateTime, Auto-generated)

- **Validation**:
  - Role must be either "user" or "assistant"
  - Content must not be empty
  - Conversation must exist

- **Relationships**:
  - Belongs to one Conversation
  - Conversation has many Messages
  - Belongs to one User

## Entity: User
- **Fields**:
  - id (String, Primary Key, UUID)
  - email (String, Unique, Required)
  - name (String, Optional)
  - created_at (DateTime, Auto-generated)
  - updated_at (DateTime, Auto-generated)

- **Validation**:
  - Email must be valid format
  - Email must be unique

- **Relationships**:
  - Has many Tasks
  - Has many Conversations
  - Has many Messages