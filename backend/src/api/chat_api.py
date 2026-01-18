from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import Response
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uuid
from datetime import datetime
from ..services.conversation_service import ConversationService
from ..services.task_service import TaskService
from ..database import get_session
from sqlmodel import Session
import os
from ..logging_config import logger
from .dependencies import get_current_user, verify_user_access
from ..models import User
from ..security_config import limiter, RATE_LIMIT_CHAT
from ..config import get_settings

# Import services with error handling
def _import_services():
    """Safely import services that may not exist"""
    RAGService = None
    MCPTaskTools = None

    try:
        from ..services.rag_service import RAGService as ImportedRAGService
        RAGService = ImportedRAGService
    except ImportError as e:
        logger.error(f"Failed to import RAGService: {str(e)}")
        RAGService = None

    try:
        from ..mcp.tools import MCPTaskTools as ImportedMCPTaskTools
        MCPTaskTools = ImportedMCPTaskTools
    except ImportError as e:
        logger.error(f"Failed to import MCPTaskTools: {str(e)}")
        MCPTaskTools = None

    return RAGService, MCPTaskTools

RAGService, MCPTaskTools = _import_services()

# Load settings
settings = get_settings()

router = APIRouter(prefix="/api", tags=["chat"])

# Request and Response Models
class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str


class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: List[ToolCall] = []


# Initialize RAG service
try:
    cohere_api_key = settings.cohere_api_key
    if not cohere_api_key:
        # Log warning but don't raise an exception to allow the app to start
        logger.warning("COHERE_API_KEY environment variable is not set. Chat functionality will be disabled.")
        rag_service = None
    else:
        rag_service = RAGService(cohere_api_key)
except Exception as e:
    logger.error(f"Error initializing RAG service: {str(e)}")
    rag_service = None


def generate_basic_response(user_message: str, tasks: list) -> str:
    """
    Generate a basic response when RAG service is unavailable.
    Provides helpful responses based on message content and user's tasks.
    """
    import re

    message_lower = user_message.lower()

    # Check for task-related keywords
    if any(keyword in message_lower for keyword in ["task", "todo", "to do", "list", "show"]):
        if tasks:
            task_count = len(tasks)
            completed_tasks = len([task for task in tasks if getattr(task, 'completed', False)])
            return f"I can see you have {task_count} tasks in total, with {completed_tasks} completed. You can ask me to list your tasks or help manage them!"
        else:
            return "You don't have any tasks yet. You can ask me to help you create some tasks!"

    # Check for greeting
    elif any(greeting in message_lower for greeting in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I'm your task management assistant. I can help you create, list, update, and manage your tasks. What would you like to do today?"

    # Check for help request
    elif any(help_word in message_lower for help_word in ["help", "what can you do", "how to", "assist"]):
        return "I can help you manage your tasks! You can ask me to: add a task, list your tasks, complete a task, update a task, or delete a task. For example: 'Add a task to buy groceries' or 'Show me my tasks'."

    # Check for adding tasks
    elif any(add_word in message_lower for add_word in ["add", "create", "new", "make"]):
        return "Sure! I can help you add a task. Please specify what task you'd like to add. For example: 'Add a task to call John tomorrow' or 'Create a task to finish the report'."

    # Check for completion
    elif any(complete_word in message_lower for complete_word in ["complete", "done", "finish", "mark"]):
        return "I can help you mark tasks as complete. Please specify which task you'd like to mark as complete. For example: 'Mark task 1 as complete' or 'Complete the grocery task'."

    # Default response
    else:
        return "I'm your task management assistant. I'm currently operating in basic mode. You can ask me to help with your tasks like adding, listing, or completing them. For example: 'Add a task to water the plants' or 'Show me my tasks'."


@router.post("/{user_id}/chat", response_model=ChatResponse)
# @limiter.limit(RATE_LIMIT_CHAT)  # Temporarily disabled to fix the request object conflict
async def chat_endpoint(
    request: Request,  # FastAPI request object for rate limiter
    user_id: str,
    chat_request: ChatRequest,  # Renamed to avoid conflict with rate limiter
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """
    Initiates or continues a conversation with the RAG-enhanced chatbot for todo management.

    Processes a user's natural language message and returns an appropriate response.
    The system may invoke MCP tools based on the user's intent.
    If conversation_id is not provided, a new conversation is created.
    """
    # Verify that the authenticated user matches the user_id in the path
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: user ID mismatch"
        )

    logger.info(f"Chat endpoint called for user {user_id} with message: {chat_request.message[:50]}...")

    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        # Get or create conversation
        if not chat_request.conversation_id:
            logger.info(f"Creating new conversation for user {user_id}")
            conversation = ConversationService.create_conversation(session, user_id)
            conversation_id = str(conversation.id)
        else:
            conversation_id = chat_request.conversation_id
            # Verify conversation belongs to user
            conversation = ConversationService.get_conversation(session, conversation_id, user_id)
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found for user {user_id}")
                raise HTTPException(status_code=404, detail="Conversation not found")

        # Add user message to conversation
        user_message = ConversationService.add_message(
            session=session,
            conversation_id=conversation_id,
            user_id=user_id,
            content=chat_request.message,
            role="user"
        )
        logger.info(f"Added user message to conversation {conversation_id}")

        # Get conversation history for context (enhanced loading)
        messages = ConversationService.get_conversation_messages(session, conversation_id, user_id)

        # Get user's tasks for context
        tasks = TaskService.get_tasks(session, user_id)

        # Enhanced context loading - get more comprehensive history
        # Load recent conversations for broader context
        recent_conversations = ConversationService.get_recent_conversations(session, user_id, limit=5)

        # Check if RAG service is available
        if rag_service:
            try:
                import asyncio
                import concurrent.futures
                from functools import partial

                # Set shorter timeout for RAG operations (5 seconds to ensure quick responses)
                def run_rag_operations():
                    # Retrieve context using RAG (enhanced with more detailed context)
                    context = rag_service.retrieve_context(user_id, chat_request.message, tasks, messages, recent_conversations)
                    logger.info(f"RAG context retrieved for user {user_id}")

                    # Generate response using RAG
                    response = rag_service.generate_response(user_id, chat_request.message, context)
                    logger.info(f"RAG response generated for user {user_id}")
                    return response

                # Execute RAG operations with shorter timeout
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_rag_operations)
                    response_text = future.result(timeout=5.0)  # 5 second timeout

            except concurrent.futures.TimeoutError:
                logger.warning(f"RAG service timed out for user {user_id}")
                # Use basic response when RAG service times out
                response_text = generate_basic_response(chat_request.message, tasks)
            except Exception as e:
                logger.error(f"Error using RAG service for user {user_id}: {str(e)}")
                # Use basic response when RAG service fails
                response_text = generate_basic_response(chat_request.message, tasks)
        else:
            # Use basic response when RAG service is not available
            logger.warning(f"RAG service not available for user {user_id}, using basic response")
            response_text = generate_basic_response(chat_request.message, tasks)

        # Detect intent and call appropriate MCP tools
        tool_calls = []
        invoked_responses = []

        # Enhanced intent detection with context awareness
        message_lower = chat_request.message.lower()

        # Enhanced add task intent with metadata extraction
        if any(word in message_lower for word in ["add", "create", "new", "task", "remember", "make", "set up", "put in", "schedule", "plan"]):
            # Extract task title and metadata from message using more sophisticated parsing
            import re

            # More comprehensive title extraction patterns
            title_match = None
            title_patterns = [
                r"(?:add|create|remember|make|set up|put in|schedule|plan|note|record|remind me to|need to|have to|i should|to do).*?(?:task|to|that|about|for|on|by)?\s+(.+?)(?:\s+(?:with|due|by|on|at|for|and|or|but|when)|$)",
                r"(?:add|create|remember|make|set up|put in|schedule|plan|note|record|remind me to|need to|have to|i should|to do)\s+(.+?)(?:\s+(?:with|due|by|on|at|for|and|or|but|when)|$)",
                r"(?:i need to|i have to|must|should|want to|going to)\s+(.+?)(?:\s+(?:with|due|by|on|at|for|and|or|but|when)|$)"
            ]

            for pattern in title_patterns:
                title_match = re.search(pattern, message_lower)
                if title_match:
                    break

            task_title = title_match.group(1).strip() if title_match else None

            # Extract priority with more variations
            priority = None
            if any(word in message_lower for word in ["high priority", "high-priority", "urgent", "asap", "immediately", "right away", "top priority", "critical", "important"]):
                priority = "HIGH"
            elif any(word in message_lower for word in ["low priority", "low-priority", "not urgent", "whenever", "whenever convenient", "not important", "can wait"]):
                priority = "LOW"
            elif any(word in message_lower for word in ["medium priority", "medium-priority", "normal priority", "regular priority"]):
                priority = "MEDIUM"

            # Extract category with more variations
            category = None
            if any(word in message_lower for word in ["work", "meeting", "office", "job", "career", "professional", "business", "colleagues", "team", "project"]):
                category = "WORK"
            elif any(word in message_lower for word in ["personal", "family", "me", "myself", "private", "home", "household", "chores", "friends"]):
                category = "PERSONAL"
            elif any(word in message_lower for word in ["shop", "buy", "grocery", "purchase", "market", "store", "shopping list", "errands"]):
                category = "SHOPPING"
            elif any(word in message_lower for word in ["health", "doctor", "exercise", "fitness", "medical", "appointment", "wellness", "medicine", "hospital"]):
                category = "HEALTH"
            elif any(word in message_lower for word in ["finance", "money", "bill", "payment", "bank", "tax", "investment", "budget", "expense"]):
                category = "FINANCE"

            # Extract due date with more patterns
            due_date = None
            # Look for date patterns like "due tomorrow", "by Friday", "on 2023-12-25", etc.
            date_patterns = [
                r"due\s+(tomorrow|today|tonight|this week|next week|this weekend|next weekend|this month|next month)",
                r"by\s+(tomorrow|today|tonight|this week|next week|this weekend|next weekend|this month|next month)",
                r"on\s+(tomorrow|today|tonight|monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|march|april|may|june|july|august|september|october|november|december)\s*(\d{1,2})?",
                r"on\s+(\d{4}-\d{2}-\d{2})",
                r"in\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)",
                r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(this|next)\s+week",
                r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?"
            ]
            for pattern in date_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    # In a real implementation, we would parse these into actual dates
                    # For now, we'll just note that a date was mentioned
                    due_date = str(datetime.utcnow().date())  # Placeholder
                    break

            # Extract estimated duration
            estimated_duration = None
            duration_patterns = [
                r"(\d+)\s+(minute|minutes|min|hour|hours|hr|hrs)",
                r"takes?\s+about\s+(\d+)\s+(minute|minutes|min|hour|hours|hr|hrs)",
                r"will take\s+(\d+)\s+(minute|minutes|min|hour|hours|hr|hrs)"
            ]
            for pattern in duration_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    num = int(match.group(1))
                    unit = match.group(2)
                    if "hour" in unit or "hr" in unit:
                        estimated_duration = num * 60  # Convert to minutes
                    else:
                        estimated_duration = num
                    break

            # Extract additional metadata
            tags = None
            tag_match = re.search(r"with tags?\s+([^.!?]+)", message_lower)
            if tag_match:
                tags = tag_match.group(1).strip()

            # Extract status
            status = None
            if "in progress" in message_lower or "working on" in message_lower:
                status = "in_progress"
            elif "review" in message_lower or "checking" in message_lower:
                status = "review"
            elif "done" in message_lower or "completed" in message_lower:
                status = "done"

            if task_title:
                if MCPTaskTools is not None:
                    try:
                        logger.info(f"Calling add_task for user {user_id} with title: {task_title}, priority: {priority}, category: {category}, duration: {estimated_duration}")
                        result = MCPTaskTools.add_task(
                            user_id, task_title,
                            priority=priority,
                            category=category,
                            due_date=due_date,
                            estimated_duration_minutes=estimated_duration,
                            tags=tags,
                            status=status
                        )
                        tool_call_args = {
                            "user_id": user_id,
                            "title": task_title
                        }
                        if priority:
                            tool_call_args["priority"] = priority
                        if category:
                            tool_call_args["category"] = category
                        if due_date:
                            tool_call_args["due_date"] = due_date
                        if estimated_duration:
                            tool_call_args["estimated_duration_minutes"] = estimated_duration
                        if tags:
                            tool_call_args["tags"] = tags
                        if status:
                            tool_call_args["status"] = status

                        tool_calls.append(ToolCall(tool_name="add_task", arguments=tool_call_args))
                        invoked_responses.append(result)
                    except Exception as e:
                        logger.error(f"Error calling add_task: {str(e)}")
                        response_text = f"Error adding task: {str(e)}"
                else:
                    logger.warning("MCPTaskTools not available, skipping add_task operation")
                    response_text = f"Task '{task_title}' could not be added because the task service is not available."

        # Enhanced list tasks intent with advanced filtering
        elif any(word in message_lower for word in ["list", "show", "view", "see", "my", "tasks"]):
            status = None
            priority = None
            category = None
            due_before = None
            search_term = None
            task_status = None
            tags = None
            parent_task_id = None
            completed = None

            # Determine status
            if "completed" in message_lower:
                completed = True
            elif "pending" in message_lower or "incomplete" in message_lower or "not done" in message_lower:
                completed = False
            elif "all" in message_lower:
                completed = None

            # Determine task status
            if "in progress" in message_lower or "working on" in message_lower:
                task_status = "in_progress"
            elif "review" in message_lower:
                task_status = "review"
            elif "todo" in message_lower or "to do" in message_lower:
                task_status = "todo"
            elif "done" in message_lower:
                task_status = "done"

            # Determine priority
            if "high priority" in message_lower or "high-priority" in message_lower:
                priority = "HIGH"
            elif "low priority" in message_lower or "low-priority" in message_lower:
                priority = "LOW"
            elif "medium priority" in message_lower or "medium-priority" in message_lower:
                priority = "MEDIUM"

            # Determine category
            if "work" in message_lower:
                category = "WORK"
            elif "personal" in message_lower:
                category = "PERSONAL"
            elif "shopping" in message_lower or "buy" in message_lower:
                category = "SHOPPING"
            elif "health" in message_lower or "medical" in message_lower or "doctor" in message_lower:
                category = "HEALTH"
            elif "finance" in message_lower or "money" in message_lower or "bill" in message_lower:
                category = "FINANCE"

            # Determine tags
            tag_match = re.search(r"with tags?\s+([^.!?]+)", message_lower)
            if tag_match:
                tags = tag_match.group(1).strip()

            # Determine due date filters
            if "overdue" in message_lower:
                if MCPTaskTools is not None:
                    # Special case - get overdue tasks
                    try:
                        logger.info(f"Calling list_overdue_tasks for user {user_id}")
                        result = MCPTaskTools.list_overdue_tasks(user_id)
                        tool_calls.append(ToolCall(tool_name="list_overdue_tasks", arguments={
                            "user_id": user_id
                        }))
                        invoked_responses.append(result)

                        # Enhance response with task information
                        task_count = len(result.get("tasks", []))
                        if task_count > 0:
                            response_text = f"I found {task_count} overdue tasks for you. {response_text}"
                        else:
                            response_text = f"You have no overdue tasks. {response_text}"
                    except Exception as e:
                        logger.error(f"Error calling list_overdue_tasks: {str(e)}")
                        response_text = f"Error listing overdue tasks: {str(e)}"
                else:
                    logger.warning("MCPTaskTools not available, skipping list_overdue_tasks operation")
                    response_text = f"Cannot list overdue tasks because the task service is not available. {response_text}"
            else:
                if MCPTaskTools is not None:
                    # Handle regular list tasks with filters
                    try:
                        logger.info(f"Calling list_tasks for user {user_id} with filters: status={status}, priority={priority}, category={category}, task_status={task_status}, tags={tags}")
                        result = MCPTaskTools.list_tasks(user_id, status, priority, category, due_before, search_term, task_status=task_status, tags=tags, completed=completed)
                        tool_call_args = {
                            "user_id": user_id
                        }
                        if status:
                            tool_call_args["status"] = status
                        if priority:
                            tool_call_args["priority"] = priority
                        if category:
                            tool_call_args["category"] = category
                        if task_status:
                            tool_call_args["task_status"] = task_status
                        if tags:
                            tool_call_args["tags"] = tags
                        if completed is not None:
                            tool_call_args["completed"] = completed

                        tool_calls.append(ToolCall(tool_name="list_tasks", arguments=tool_call_args))
                        invoked_responses.append(result)

                        # Enhance response with task information
                        task_count = len(result.get("tasks", []))
                        response_text = f"I found {task_count} tasks for you. {response_text}"
                    except Exception as e:
                        logger.error(f"Error calling list_tasks: {str(e)}")
                        response_text = f"Error listing tasks: {str(e)}"
                else:
                    logger.warning("MCPTaskTools not available, skipping list_tasks operation")
                    response_text = f"Cannot list tasks because the task service is not available. {response_text}"

        # Complete task intent
        elif any(word in message_lower for word in ["complete", "done", "finish", "mark"]):
            # Try to extract task ID from message
            import re
            task_id_match = re.search(r"task\s+(\d+)|(\d+)\s+task", message_lower)
            if task_id_match:
                task_id = int(task_id_match.group(1) or task_id_match.group(2))
                if MCPTaskTools is not None:
                    try:
                        logger.info(f"Calling complete_task for user {user_id}, task ID: {task_id}")
                        result = MCPTaskTools.complete_task(user_id, task_id)
                        tool_calls.append(ToolCall(tool_name="complete_task", arguments={
                            "user_id": user_id,
                            "task_id": task_id
                        }))
                        invoked_responses.append(result)

                        response_text = f"I've marked task #{task_id} as complete. {response_text}"
                    except Exception as e:
                        logger.error(f"Error calling complete_task: {str(e)}")
                        response_text = f"Error completing task: {str(e)}"
                else:
                    logger.warning("MCPTaskTools not available, skipping complete_task operation")
                    response_text = f"Cannot complete task #{task_id} because the task service is not available. {response_text}"

        # Delete task intent
        elif any(word in message_lower for word in ["delete", "remove", "cancel"]):
            # Try to extract task ID from message
            import re
            task_id_match = re.search(r"task\s+(\d+)|(\d+)\s+task", message_lower)
            if task_id_match:
                task_id = int(task_id_match.group(1) or task_id_match.group(2))
                if MCPTaskTools is not None:
                    try:
                        logger.info(f"Calling delete_task for user {user_id}, task ID: {task_id}")
                        result = MCPTaskTools.delete_task(user_id, task_id)
                        tool_calls.append(ToolCall(tool_name="delete_task", arguments={
                            "user_id": user_id,
                            "task_id": task_id
                        }))
                        invoked_responses.append(result)

                        response_text = f"I've deleted task #{task_id}. {response_text}"
                    except Exception as e:
                        logger.error(f"Error calling delete_task: {str(e)}")
                        response_text = f"Error deleting task: {str(e)}"
                else:
                    logger.warning("MCPTaskTools not available, skipping delete_task operation")
                    response_text = f"Cannot delete task #{task_id} because the task service is not available. {response_text}"

        # Enhanced update task intent with support for all fields
        elif any(word in message_lower for word in ["update", "change", "modify", "edit"]):
            # Try to extract task ID and new values from message
            import re
            task_id_match = re.search(r"task\s+(\d+)|(\d+)\s+task", message_lower)
            if task_id_match:
                task_id = int(task_id_match.group(1) or task_id_match.group(2))

                # Extract new title if present
                new_title = None
                title_match = re.search(r"(?:to|as|called)\s+(.+?)(?:\s+and|\s+with|\s+because|$)", message_lower)
                if title_match:
                    new_title = title_match.group(1).strip()

                # Extract new priority if present
                new_priority = None
                if "high priority" in message_lower or "urgent" in message_lower:
                    new_priority = "HIGH"
                elif "low priority" in message_lower or "not urgent" in message_lower:
                    new_priority = "LOW"
                elif "medium priority" in message_lower:
                    new_priority = "MEDIUM"

                # Extract new category if present
                new_category = None
                if "work" in message_lower:
                    new_category = "WORK"
                elif "personal" in message_lower:
                    new_category = "PERSONAL"
                elif "shopping" in message_lower or "buy" in message_lower:
                    new_category = "SHOPPING"
                elif "health" in message_lower or "medical" in message_lower or "doctor" in message_lower:
                    new_category = "HEALTH"
                elif "finance" in message_lower or "money" in message_lower or "bill" in message_lower:
                    new_category = "FINANCE"

                # Extract new status if present
                new_status = None
                if "in progress" in message_lower or "working on" in message_lower:
                    new_status = "in_progress"
                elif "review" in message_lower:
                    new_status = "review"
                elif "todo" in message_lower or "to do" in message_lower:
                    new_status = "todo"
                elif "done" in message_lower:
                    new_status = "done"

                # Extract due date if present
                new_due_date = None
                date_match = re.search(r"(?:due|by|on)\s+(\d{4}-\d{2}-\d{2})", message_lower)
                if date_match:
                    new_due_date = date_match.group(1)

                # Extract tags if present
                new_tags = None
                tag_match = re.search(r"with tags?\s+([^.!?]+)", message_lower)
                if tag_match:
                    new_tags = tag_match.group(1).strip()

                # Build arguments for update_task
                update_args = {
                    "user_id": user_id,
                    "task_id": task_id
                }

                if new_title:
                    update_args["title"] = new_title
                if new_priority:
                    update_args["priority"] = new_priority
                if new_category:
                    update_args["category"] = new_category
                if new_status:
                    update_args["status"] = new_status
                if new_due_date:
                    update_args["due_date"] = new_due_date
                if new_tags:
                    update_args["tags"] = new_tags

                if MCPTaskTools is not None:
                    try:
                        logger.info(f"Calling update_task for user {user_id}, task ID: {task_id}, with args: {update_args}")
                        result = MCPTaskTools.update_task(**update_args)
                        tool_calls.append(ToolCall(tool_name="update_task", arguments=update_args))
                        invoked_responses.append(result)

                        response_parts = [f"I've updated task #{task_id}."]
                        if new_title:
                            response_parts.append(f"The title is now '{new_title}'.")
                        if new_priority:
                            response_parts.append(f"Its priority is now {new_priority.lower()}.")
                        if new_category:
                            response_parts.append(f"Its category is now {new_category.lower()}.")
                        if new_status:
                            response_parts.append(f"Its status is now {new_status.replace('_', ' ')}.")
                        if new_due_date:
                            response_parts.append(f"Its due date is now {new_due_date}.")
                        if new_tags:
                            response_parts.append(f"Its tags are now '{new_tags}'.")

                        response_text = " ".join(response_parts) + f" {response_text}"
                    except Exception as e:
                        logger.error(f"Error calling update_task: {str(e)}")
                        response_text = f"Error updating task: {str(e)}"
                else:
                    logger.warning("MCPTaskTools not available, skipping update_task operation")
                    response_text = f"Cannot update task #{task_id} because the task service is not available. {response_text}"

        # Enhanced complex command: Create subtask
        elif any(word in message_lower for word in ["subtask", "child task", "under task"]):
            # Extract parent task ID and subtask details
            import re
            parent_task_match = re.search(r"under task\s+(\d+)|subtask of task\s+(\d+)", message_lower)
            if parent_task_match:
                parent_task_id = int(parent_task_match.group(1) or parent_task_match.group(2))

                # Extract subtask title
                subtask_title_match = re.search(r"(?:add|create|make)\s+a?\s*subtask\s+(?:for|to|of|under)\s+(?:task\s+\d+\s+)?(.+?)(?:\s+with|\s+and|\s+that|\s+which|\s+to|\s+for|$)", message_lower)
                if subtask_title_match:
                    subtask_title = subtask_title_match.group(1).strip()

                    # Extract other metadata as needed
                    priority = None
                    if any(word in message_lower for word in ["high priority", "urgent", "asap"]):
                        priority = "HIGH"
                    elif any(word in message_lower for word in ["low priority", "not urgent"]):
                        priority = "LOW"
                    elif any(word in message_lower for word in ["medium priority"]):
                        priority = "MEDIUM"

                    if subtask_title:
                        if MCPTaskTools is not None:
                            try:
                                logger.info(f"Calling add_task for user {user_id} with subtask title: {subtask_title}, parent_task_id: {parent_task_id}")
                                result = MCPTaskTools.add_task(
                                    user_id, subtask_title,
                                    priority=priority,
                                    parent_task_id=parent_task_id
                                )
                                tool_call_args = {
                                    "user_id": user_id,
                                    "title": subtask_title,
                                    "parent_task_id": parent_task_id
                                }
                                if priority:
                                    tool_call_args["priority"] = priority

                                tool_calls.append(ToolCall(tool_name="add_task", arguments=tool_call_args))
                                invoked_responses.append(result)

                                response_text = f"I've created a subtask '{subtask_title}' under task #{parent_task_id}. {response_text}"
                            except Exception as e:
                                logger.error(f"Error creating subtask: {str(e)}")
                                response_text = f"Error creating subtask: {str(e)}"
                        else:
                            logger.warning("MCPTaskTools not available, skipping subtask creation")
                            response_text = f"Cannot create subtask '{subtask_title}' because the task service is not available. {response_text}"

        # Enhanced context-aware processing for follow-up questions
        # Check if the message refers to a previous task without explicit ID
        if any(word in message_lower for word in ["it", "that", "the task", "the one", "previous", "earlier", "above", "mentioned"]):
            # If user refers to a previous task without ID, try to infer from context
            try:
                all_tasks = TaskService.get_tasks(session, user_id)

                # Only try to extract task reference if rag_service is available
                referenced_task = None
                try:
                    if rag_service:
                        referenced_task = rag_service.extract_task_reference(chat_request.message, all_tasks)
                except Exception as e:
                    logger.error(f"Error extracting task reference: {str(e)}")

                # Handle different types of operations based on context
                if any(word in message_lower for word in ["complete", "done", "finish", "mark"]):
                    if MCPTaskTools is not None:
                        if referenced_task:
                            try:
                                result = MCPTaskTools.complete_task(user_id, referenced_task.id)
                                tool_calls.append(ToolCall(tool_name="complete_task", arguments={
                                    "user_id": user_id,
                                    "task_id": referenced_task.id
                                }))
                                response_text = f"I've marked '{referenced_task.title}' as complete. {response_text}"
                            except Exception as e:
                                logger.error(f"Error completing referenced task: {str(e)}")
                                response_text = f"Error completing task: {str(e)}"
                        else:
                            # If no specific task identified, find the most recent incomplete task
                            try:
                                pending_tasks = MCPTaskTools.list_tasks(user_id, status="pending")
                                if pending_tasks.get("tasks"):
                                    latest_task = pending_tasks["tasks"][-1]  # Most recent task
                                    result = MCPTaskTools.complete_task(user_id, latest_task["id"])
                                    tool_calls.append(ToolCall(tool_name="complete_task", arguments={
                                        "user_id": user_id,
                                        "task_id": latest_task["id"]
                                    }))
                                    response_text = f"I've marked '{latest_task['title']}' as complete. {response_text}"
                            except Exception as e:
                                logger.error(f"Error completing latest task: {str(e)}")
                                response_text = f"Error completing task: {str(e)}"
                    else:
                        logger.warning("MCPTaskTools not available, skipping complete task operation in context-aware processing")
                        response_text = f"Cannot complete task because the task service is not available. {response_text}"

                elif any(word in message_lower for word in ["delete", "remove", "cancel"]):
                    if MCPTaskTools is not None:
                        if referenced_task:
                            try:
                                result = MCPTaskTools.delete_task(user_id, referenced_task.id)
                                tool_calls.append(ToolCall(tool_name="delete_task", arguments={
                                    "user_id": user_id,
                                    "task_id": referenced_task.id
                                }))
                                response_text = f"I've deleted '{referenced_task.title}'. {response_text}"
                            except Exception as e:
                                logger.error(f"Error deleting referenced task: {str(e)}")
                                response_text = f"Error deleting task: {str(e)}"
                        else:
                            # Find the most recently created task
                            try:
                                all_user_tasks = MCPTaskTools.list_tasks(user_id)
                                if all_user_tasks.get("tasks"):
                                    latest_task = all_user_tasks["tasks"][-1]  # Most recent task
                                    result = MCPTaskTools.delete_task(user_id, latest_task["id"])
                                    tool_calls.append(ToolCall(tool_name="delete_task", arguments={
                                        "user_id": user_id,
                                        "task_id": latest_task["id"]
                                    }))
                                    response_text = f"I've deleted '{latest_task['title']}'. {response_text}"
                            except Exception as e:
                                logger.error(f"Error deleting latest task: {str(e)}")
                                response_text = f"Error deleting task: {str(e)}"
                    else:
                        logger.warning("MCPTaskTools not available, skipping delete task operation in context-aware processing")
                        response_text = f"Cannot delete task because the task service is not available. {response_text}"

                elif any(word in message_lower for word in ["update", "change", "modify", "edit"]):
                    if referenced_task:
                        # Extract what needs to be updated from the message
                        import re

                        # Extract new title if present
                        new_title = None
                        title_match = re.search(r"(?:to|as|called)\s+(.+?)(?:\s+and|\s+with|\s+because|$)", message_lower)
                        if title_match:
                            new_title = title_match.group(1).strip()

                        # Extract new priority if present
                        new_priority = None
                        if "high priority" in message_lower or "urgent" in message_lower:
                            new_priority = "HIGH"
                        elif "low priority" in message_lower or "not urgent" in message_lower:
                            new_priority = "LOW"
                        elif "medium priority" in message_lower:
                            new_priority = "MEDIUM"

                        # Extract new category if present
                        new_category = None
                        if "work" in message_lower:
                            new_category = "WORK"
                        elif "personal" in message_lower:
                            new_category = "PERSONAL"
                        elif "shopping" in message_lower or "buy" in message_lower:
                            new_category = "SHOPPING"
                        elif "health" in message_lower or "medical" in message_lower or "doctor" in message_lower:
                            new_category = "HEALTH"
                        elif "finance" in message_lower or "money" in message_lower or "bill" in message_lower:
                            new_category = "FINANCE"

                        # Extract due date if present
                        new_due_date = None
                        date_match = re.search(r"(?:due|by|on)\s+(\d{4}-\d{2}-\d{2})", message_lower)
                        if date_match:
                            new_due_date = date_match.group(1)

                        # Build arguments for update_task
                        update_args = {
                            "user_id": user_id,
                            "task_id": referenced_task.id
                        }

                        if new_title:
                            update_args["title"] = new_title
                        if new_priority:
                            update_args["priority"] = new_priority
                        if new_category:
                            update_args["category"] = new_category
                        if new_due_date:
                            update_args["due_date"] = new_due_date

                        if MCPTaskTools is not None:
                            result = MCPTaskTools.update_task(**update_args)
                            tool_calls.append(ToolCall(tool_name="update_task", arguments=update_args))

                            response_parts = [f"I've updated '{referenced_task.title}'."]
                            if new_title:
                                response_parts.append(f"The title is now '{new_title}'.")
                            if new_priority:
                                response_parts.append(f"Its priority is now {new_priority.lower()}.")
                            if new_category:
                                response_parts.append(f"Its category is now {new_category.lower()}.")
                            if new_due_date:
                                response_parts.append(f"Its due date is now {new_due_date}.")

                            response_text = " ".join(response_parts) + f" {response_text}"
                        else:
                            logger.warning("MCPTaskTools not available, skipping update_task operation")
                            response_text = f"Cannot update '{referenced_task.title}' because the task service is not available. {response_text}"
                    else:
                        # If no specific task identified, inform the user
                        response_text = f"Sorry, I couldn't identify which task you wanted to update. Could you please specify the task more clearly? {response_text}"
            except Exception as e:
                logger.error(f"Error processing referenced task: {str(e)}")
                response_text = f"Sorry, I couldn't identify which task you meant. Could you please specify the task more clearly? {response_text}"

        # Add assistant message to conversation
        ConversationService.add_message(
            session=session,
            conversation_id=conversation_id,
            user_id=user_id,
            content=response_text,
            role="assistant"
        )
        logger.info(f"Added assistant response to conversation {conversation_id}")

        response = ChatResponse(
            conversation_id=conversation_id,
            response=response_text,
            tool_calls=tool_calls
        )
        logger.info(f"Returning response for user {user_id}, conversation {conversation_id}")
        return response

    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint for user {user_id}: {str(e)}")
        raise
    finally:
        session.close()


@router.get("/{user_id}/conversations")
@limiter.limit(RATE_LIMIT_CHAT)
async def get_user_conversations(
    request: Request,
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a list of conversation IDs for the user.
    """
    # Verify that the authenticated user matches the user_id in the path
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: user ID mismatch"
        )

    logger.info(f"Getting conversations for user {user_id}")

    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        conversations = ConversationService.get_user_conversations(session, user_id)
        conversation_list = []
        for conv in conversations:
            conversation_list.append({
                "id": str(conv.id),
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            })
        logger.info(f"Returning {len(conversation_list)} conversations for user {user_id}")
        return {"conversations": conversation_list}

    except Exception as e:
        logger.error(f"Error getting conversations for user {user_id}: {str(e)}")
        raise
    finally:
        session.close()


@router.get("/{user_id}/conversations/{conversation_id}/messages")
@limiter.limit(RATE_LIMIT_CHAT)
async def get_conversation_messages(
    request: Request,
    user_id: str,
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves messages from a specific conversation.
    """
    # Verify that the authenticated user matches the user_id in the path
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: user ID mismatch"
        )

    logger.info(f"Getting messages for user {user_id}, conversation {conversation_id}")

    session_gen = get_session()
    session: Session = next(session_gen)

    try:
        messages = ConversationService.get_conversation_messages(session, conversation_id, user_id)
        message_list = []
        for msg in messages:
            message_list.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            })
        logger.info(f"Returning {len(message_list)} messages for user {user_id}, conversation {conversation_id}")
        return {"messages": message_list}

    except Exception as e:
        logger.error(f"Error getting messages for user {user_id}, conversation {conversation_id}: {str(e)}")
        raise
    finally:
        session.close()


# Explicitly handle OPTIONS requests for CORS - without authentication dependencies
@router.options("/{user_id}/chat", include_in_schema=False)
async def options_chat(user_id: str):
    """
    Handle OPTIONS request for chat endpoint.
    This ensures proper CORS handling without authentication.
    """
    response = Response()
    response.headers["Allow"] = "POST, OPTIONS"
    return response


@router.options("/{user_id}/conversations", include_in_schema=False)
async def options_conversations(user_id: str):
    """
    Handle OPTIONS request for conversations endpoint.
    This ensures proper CORS handling without authentication.
    """
    response = Response()
    response.headers["Allow"] = "GET, OPTIONS"
    return response


@router.options("/{user_id}/conversations/{conversation_id}/messages", include_in_schema=False)
async def options_conversation_messages(user_id: str, conversation_id: str):
    """
    Handle OPTIONS request for conversation messages endpoint.
    This ensures proper CORS handling without authentication.
    """
    response = Response()
    response.headers["Allow"] = "GET, OPTIONS"
    return response