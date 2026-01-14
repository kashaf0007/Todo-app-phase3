import cohere
from typing import List, Dict, Any
from ..models.task import Task
from ..models.message import Message
from ..models.conversation import Conversation
from datetime import datetime
from ..logging_config import logger


class RAGService:
    def __init__(self, api_key: str):
        self.co = cohere.Client(api_key)

    def retrieve_context(self, user_id: str, query: str, tasks: List[Task], messages: List[Message], recent_conversations: List[Conversation] = None) -> str:
        """
        Retrieve relevant context from user's tasks and conversation history
        """
        logger.info(f"RAGService.retrieve_context called for user {user_id}")

        # Combine tasks and messages into a context string
        context_parts = []

        # Add recent tasks with more detailed information
        if tasks:
            context_parts.append("USER TASKS:")
            for task in tasks[-10:]:  # Last 10 tasks for more comprehensive context
                status = "COMPLETED" if task.completed else "PENDING"
                created_date = task.created_at.strftime("%Y-%m-%d")
                context_parts.append(f"  - ID: {task.id}, Title: '{task.title}', Status: {status}, Created: {created_date}")
                if task.description:
                    context_parts.append(f"    Description: {task.description}")

        # Add recent conversation history with better formatting
        if messages:
            context_parts.append("\nCONVERSATION HISTORY:")
            for msg in messages[-15:]:  # Last 15 messages for richer context
                timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
                context_parts.append(f"  [{timestamp}] {msg.role.upper()}: {msg.content}")

        # Add recent conversations for broader context if provided
        if recent_conversations:
            context_parts.append("\nRECENT CONVERSATIONS:")
            for conv in recent_conversations[-5:]:  # Last 5 conversations
                updated_date = conv.updated_at.strftime("%Y-%m-%d %H:%M")
                context_parts.append(f"  - Conversation ID: {conv.id}, Updated: {updated_date}")
                if conv.title:
                    context_parts.append(f"    Title: {conv.title}")

        context_str = "\n".join(context_parts)

        # Use Cohere's rerank or generate to find most relevant context
        if context_str:
            try:
                # Generate a summary of the context that's most relevant to the query
                response = self.co.generate(
                    model='command',
                    prompt=f"""Based on the following context, extract information relevant to this query: '{query}'

Context:
{context_str}

Provide a concise summary of the most relevant information that would help answer the user's query. Focus on:
1. Recent tasks that might be relevant
2. Previous conversation exchanges that provide context
3. Any patterns or repeated topics in the conversation
4. Broader conversation history for additional context

Relevant Information:""",
                    max_tokens=300,
                    temperature=0.1
                )
                logger.info(f"RAG context retrieved successfully for user {user_id}")
                return response.generations[0].text.strip()
            except Exception as e:
                logger.error(f"Error in RAG context retrieval for user {user_id}: {str(e)}")
                # If Cohere fails, return the raw context
                return context_str
        else:
            logger.info(f"No context available for user {user_id}")
            return ""

    def generate_response(self, user_id: str, user_message: str, context: str) -> str:
        """
        Generate a response using Cohere based on user message and context
        """
        logger.info(f"RAGService.generate_response called for user {user_id}")

        # Enhanced prompt with better context utilization
        prompt = f"""You are an intelligent task management assistant that helps users manage their todos through natural language.

CONTEXT FOR THIS CONVERSATION:
{context}

PREVIOUS USER MESSAGE: {user_message}

INSTRUCTIONS:
1. Understand the user's request in the context of their previous interactions and tasks
2. If the user refers to tasks without specifying IDs, use the context to determine which task they mean
3. Be helpful, concise, and accurate
4. If you performed an action (like creating or updating a task), acknowledge it
5. If you need clarification, ask for it

RESPONSE:"""

        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=300,
                temperature=0.7
            )
            logger.info(f"RAG response generated successfully for user {user_id}")
            return response.generations[0].text.strip()
        except Exception as e:
            logger.error(f"Error in RAG response generation for user {user_id}: {str(e)}")
            return f"Sorry, I encountered an error processing your request: {str(e)}"

    def extract_task_reference(self, user_message: str, tasks: List[Task]) -> Task:
        """
        Enhanced NLP method to extract which task the user is referring to based on the message
        """
        logger.info(f"Attempting to extract task reference from message: {user_message}")

        # Convert message to lowercase for easier matching
        message_lower = user_message.lower()

        # Look for explicit task ID references
        import re
        task_id_match = re.search(r"task\s+(\d+)|(\d+)\s+task", message_lower)
        if task_id_match:
            task_id = int(task_id_match.group(1) or task_id_match.group(2))
            for task in tasks:
                if task.id == task_id:
                    logger.info(f"Found explicit task reference: {task.id}")
                    return task

        # Look for task titles in the message (with fuzzy matching)
        for task in reversed(tasks):  # Check most recent tasks first
            task_title_lower = task.title.lower()
            if task_title_lower in message_lower:
                logger.info(f"Found exact task title reference: {task.title}")
                return task

            # Fuzzy matching for partial title matches
            task_words = set(task_title_lower.split())
            message_words = set(message_lower.split())
            common_words = task_words.intersection(message_words)

            # If more than half the words in the task title appear in the message
            if len(common_words) > 0 and len(common_words) >= len(task_words) * 0.5:
                logger.info(f"Found fuzzy task title reference: {task.title}")
                return task

        # Enhanced context reference patterns
        context_patterns = [
            # References to "that task", "the task", "it", etc.
            r"that\s+(?:task|one|thing|item)",
            r"the\s+(?:task|one|thing|item)",
            r"it(?:s|'s)?",
            r"this\s+(?:task|one|thing|item)",
            # References to previous tasks by position
            r"the\s+(?:first|second|third|last|previous)\s+task",
            # References to tasks by status
            r"the\s+(?:pending|incomplete|current|active)\s+task",
            r"the\s+(?:completed|finished|done)\s+task",
            # References to tasks by priority
            r"the\s+(?:high|medium|low)\s+priority\s+task",
            # References to tasks by category
            r"the\s+(?:work|personal|shopping|health|finance)\s+task",
        ]

        for pattern in context_patterns:
            if re.search(pattern, message_lower):
                # If user refers to a specific type of task, try to find the most appropriate one
                if "last" in message_lower or "previous" in message_lower:
                    if tasks:
                        logger.info(f"Inferring reference to last task: {tasks[-1].title}")
                        return tasks[-1]
                elif "first" in message_lower:
                    if tasks:
                        logger.info(f"Inferring reference to first task: {tasks[0].title}")
                        return tasks[0]
                elif "pending" in message_lower or "incomplete" in message_lower or "current" in message_lower or "active" in message_lower:
                    # Find the most recent pending task
                    for task in reversed(tasks):
                        if not task.completed:
                            logger.info(f"Inferring reference to pending task: {task.title}")
                            return task
                elif "completed" in message_lower or "finished" in message_lower or "done" in message_lower:
                    # Find the most recent completed task
                    for task in reversed(tasks):
                        if task.completed:
                            logger.info(f"Inferring reference to completed task: {task.title}")
                            return task
                elif "high priority" in message_lower:
                    # Find the most recent high priority task
                    for task in reversed(tasks):
                        if hasattr(task, 'priority') and task.priority == 'HIGH':
                            logger.info(f"Inferring reference to high priority task: {task.title}")
                            return task
                elif "work" in message_lower:
                    # Find the most recent work task
                    for task in reversed(tasks):
                        if hasattr(task, 'category') and task.category == 'WORK':
                            logger.info(f"Inferring reference to work task: {task.title}")
                            return task
                elif "personal" in message_lower:
                    # Find the most recent personal task
                    for task in reversed(tasks):
                        if hasattr(task, 'category') and task.category == 'PERSONAL':
                            logger.info(f"Inferring reference to personal task: {task.title}")
                            return task
                elif "shopping" in message_lower:
                    # Find the most recent shopping task
                    for task in reversed(tasks):
                        if hasattr(task, 'category') and task.category == 'SHOPPING':
                            logger.info(f"Inferring reference to shopping task: {task.title}")
                            return task
                elif "health" in message_lower:
                    # Find the most recent health task
                    for task in reversed(tasks):
                        if hasattr(task, 'category') and task.category == 'HEALTH':
                            logger.info(f"Inferring reference to health task: {task.title}")
                            return task
                elif "finance" in message_lower:
                    # Find the most recent finance task
                    for task in reversed(tasks):
                        if hasattr(task, 'category') and task.category == 'FINANCE':
                            logger.info(f"Inferring reference to finance task: {task.title}")
                            return task
                else:
                    # Default to most recent task if no specific type mentioned
                    if tasks:
                        logger.info(f"Inferring reference to most recent task: {tasks[-1].title}")
                        return tasks[-1]

        logger.info("No task reference found in message")
        return None