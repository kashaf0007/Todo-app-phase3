# API Contract: RAG Todo Chatbot

## Endpoints

### POST /api/{user_id}/chat
Initiates or continues a conversation with the RAG-enhanced chatbot for todo management.

#### Parameters
- `user_id` (path, string, required): The ID of the authenticated user

#### Request Body
```json
{
  "conversation_id": "string (optional)",
  "message": "string (required)"
}
```

#### Response
```json
{
  "conversation_id": "string",
  "response": "string",
  "tool_calls": [
    {
      "tool_name": "string",
      "arguments": "object"
    }
  ]
}
```

#### Description
Processes a user's natural language message and returns an appropriate response. The system may invoke MCP tools based on the user's intent. If conversation_id is not provided, a new conversation is created.

---

### GET /api/{user_id}/conversations
Retrieves a list of conversation IDs for the user.

#### Parameters
- `user_id` (path, string, required): The ID of the authenticated user

#### Response
```json
{
  "conversations": [
    {
      "id": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
}
```

---

### GET /api/{user_id}/conversations/{conversation_id}/messages
Retrieves messages from a specific conversation.

#### Parameters
- `user_id` (path, string, required): The ID of the authenticated user
- `conversation_id` (path, string, required): The ID of the conversation

#### Response
```json
{
  "messages": [
    {
      "id": "integer",
      "role": "string (user|assistant)",
      "content": "string",
      "created_at": "datetime"
    }
  ]
}
```

---

## MCP Tools Contract

### add_task
Creates a new task for the user.

#### Parameters
```json
{
  "user_id": "string (required)",
  "title": "string (required)",
  "description": "string (optional)"
}
```

#### Response
```json
{
  "task_id": "integer",
  "status": "string (pending|completed)",
  "title": "string"
}
```

---

### list_tasks
Retrieves tasks for the user.

#### Parameters
```json
{
  "user_id": "string (required)",
  "status": "string (optional, all|pending|completed)"
}
```

#### Response
```json
{
  "tasks": [
    {
      "id": "integer",
      "title": "string",
      "completed": "boolean",
      "description": "string"
    }
  ]
}
```

---

### complete_task
Marks a task as complete.

#### Parameters
```json
{
  "user_id": "string (required)",
  "task_id": "integer (required)"
}
```

#### Response
```json
{
  "task_id": "integer",
  "status": "string (completed)",
  "title": "string"
}
```

---

### delete_task
Removes a task.

#### Parameters
```json
{
  "user_id": "string (required)",
  "task_id": "integer (required)"
}
```

#### Response
```json
{
  "task_id": "integer",
  "status": "string (deleted)",
  "title": "string"
}
```

---

### update_task
Modifies a task's title or description.

#### Parameters
```json
{
  "user_id": "string (required)",
  "task_id": "integer (required)",
  "title": "string (optional)",
  "description": "string (optional)"
}
```

#### Response
```json
{
  "task_id": "integer",
  "status": "string (pending|completed)",
  "title": "string"
}
```