from typing import Dict, Any, Optional
from ..services.task_service import TaskService
from ..models.task import TaskBase
from sqlmodel import Session
from ..database import get_session
from ..logging_config import logger


class MCPTaskTools:
    """
    MCP tools for task operations following the contract specifications
    """

    @staticmethod
    def add_task(user_id: str, title: str, description: Optional[str] = None, priority: Optional[str] = None,
                 category: Optional[str] = None, due_date: Optional[str] = None,
                 estimated_duration_minutes: Optional[int] = None, tags: Optional[str] = None,
                 status: Optional[str] = None, parent_task_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Creates a new task for the user.

        Parameters:
        - user_id: The ID of the authenticated user
        - title: The title of the task
        - description: Optional description of the task
        - priority: Optional priority (low|medium|high)
        - category: Optional category (work|personal|shopping|health|finance|other)
        - due_date: Optional due date (ISO format string)
        - estimated_duration_minutes: Optional estimated duration in minutes
        - tags: Optional tags for the task (comma-separated)
        - status: Optional status (todo|in_progress|review|done)
        - parent_task_id: Optional parent task ID for subtasks

        Returns:
        - task_id: The ID of the created task
        - status: The status of the task (pending|completed)
        - title: The title of the task
        """
        logger.info(f"add_task called for user {user_id} with title: {title}")

        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            from datetime import datetime
            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))

        task_data = TaskBase(
            title=title,
            description=description,
            user_id=user_id,
            priority=priority,
            category=category,
            due_date=parsed_due_date,
            estimated_duration_minutes=estimated_duration_minutes,
            tags=tags,
            status=status,
            parent_task_id=parent_task_id
        )

        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            task = TaskService.create_task(session, task_data)
            result = {
                "task_id": task.id,
                "status": "completed" if task.completed else "pending",
                "title": task.title
            }
            logger.info(f"Task created successfully with ID: {task.id}")
            return result
        except Exception as e:
            logger.error(f"Error in add_task for user {user_id}: {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def list_tasks(user_id: str, status: Optional[str] = None, priority: Optional[str] = None,
                   category: Optional[str] = None, due_before: Optional[str] = None,
                   search_term: Optional[str] = None, task_status: Optional[str] = None,
                   tags: Optional[str] = None, parent_task_id: Optional[int] = None,
                   completed: Optional[bool] = None) -> Dict[str, Any]:
        """
        Retrieves tasks for the user.

        Parameters:
        - user_id: The ID of the authenticated user
        - status: Optional filter for task status (all|pending|completed) - legacy param
        - priority: Optional filter for task priority (low|medium|high)
        - category: Optional filter for task category (work|personal|shopping|health|finance|other)
        - due_before: Optional filter for tasks due before a certain date (ISO format string)
        - search_term: Optional search term to match in title or description
        - task_status: Optional filter for task status (todo|in_progress|review|done)
        - tags: Optional filter for tags (comma-separated)
        - parent_task_id: Optional filter for parent task ID
        - completed: Optional filter for completion status (True|False)

        Returns:
        - tasks: Array of task objects [{id, title, completed, description, priority, category, due_date, status, tags}]
        """
        logger.info(f"list_tasks called for user {user_id} with filters - status: {status}, priority: {priority}, category: {category}, due_before: {due_before}, search_term: {search_term}, task_status: {task_status}, tags: {tags}, parent_task_id: {parent_task_id}, completed: {completed}")

        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Parse due_before if provided
            due_before_dt = None
            if due_before:
                from datetime import datetime
                due_before_dt = datetime.fromisoformat(due_before.replace('Z', '+00:00'))

            tasks = TaskService.get_tasks(
                session, user_id, status, priority, category, due_before_dt, search_term,
                task_status=task_status, tags=tags, parent_task_id=parent_task_id, completed=completed
            )
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "description": task.description,
                    "priority": task.priority.value if task.priority else None,
                    "category": task.category.value if task.category else None,
                    "status": task.status.value if task.status else None,
                }
                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()
                if task.estimated_duration_minutes:
                    task_dict["estimated_duration_minutes"] = task.estimated_duration_minutes
                if task.tags:
                    task_dict["tags"] = task.tags
                if task.parent_task_id:
                    task_dict["parent_task_id"] = task.parent_task_id

                task_list.append(task_dict)
            logger.info(f"Returning {len(task_list)} tasks for user {user_id}")
            return {"tasks": task_list}
        except Exception as e:
            logger.error(f"Error in list_tasks for user {user_id}: {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def list_tasks_by_priority(user_id: str, priority: str) -> Dict[str, Any]:
        """
        Retrieves tasks for the user filtered by priority.

        Parameters:
        - user_id: The ID of the authenticated user
        - priority: The priority to filter by (low|medium|high)

        Returns:
        - tasks: Array of task objects [{id, title, completed, description, priority, category, due_date}]
        """
        logger.info(f"list_tasks_by_priority called for user {user_id} with priority: {priority}")

        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            tasks = TaskService.get_tasks_by_priority(session, user_id, priority)
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "description": task.description,
                    "priority": task.priority.value if task.priority else None,
                    "category": task.category.value if task.category else None,
                    "status": task.status.value if task.status else None,
                }
                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()
                if task.estimated_duration_minutes:
                    task_dict["estimated_duration_minutes"] = task.estimated_duration_minutes
                if task.tags:
                    task_dict["tags"] = task.tags
                if task.parent_task_id:
                    task_dict["parent_task_id"] = task.parent_task_id

                task_list.append(task_dict)
            logger.info(f"Returning {len(task_list)} {priority} priority tasks for user {user_id}")
            return {"tasks": task_list}
        except Exception as e:
            logger.error(f"Error in list_tasks_by_priority for user {user_id}: {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def list_tasks_by_category(user_id: str, category: str) -> Dict[str, Any]:
        """
        Retrieves tasks for the user filtered by category.

        Parameters:
        - user_id: The ID of the authenticated user
        - category: The category to filter by (work|personal|shopping|health|finance|other)

        Returns:
        - tasks: Array of task objects [{id, title, completed, description, priority, category, due_date}]
        """
        logger.info(f"list_tasks_by_category called for user {user_id} with category: {category}")

        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            tasks = TaskService.get_tasks_by_category(session, user_id, category)
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "description": task.description,
                    "priority": task.priority.value if task.priority else None,
                    "category": task.category.value if task.category else None,
                    "status": task.status.value if task.status else None,
                }
                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()
                if task.estimated_duration_minutes:
                    task_dict["estimated_duration_minutes"] = task.estimated_duration_minutes
                if task.tags:
                    task_dict["tags"] = task.tags
                if task.parent_task_id:
                    task_dict["parent_task_id"] = task.parent_task_id

                task_list.append(task_dict)
            logger.info(f"Returning {len(task_list)} {category} category tasks for user {user_id}")
            return {"tasks": task_list}
        except Exception as e:
            logger.error(f"Error in list_tasks_by_category for user {user_id}: {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def list_tasks_by_status(user_id: str, task_status: str) -> Dict[str, Any]:
        """
        Retrieves tasks for the user filtered by status.

        Parameters:
        - user_id: The ID of the authenticated user
        - task_status: The status to filter by (todo|in_progress|review|done)

        Returns:
        - tasks: Array of task objects [{id, title, completed, description, priority, category, due_date, status}]
        """
        logger.info(f"list_tasks_by_status called for user {user_id} with status: {task_status}")

        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            tasks = TaskService.get_tasks_by_status(session, user_id, task_status)
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "description": task.description,
                    "priority": task.priority.value if task.priority else None,
                    "category": task.category.value if task.category else None,
                    "status": task.status.value if task.status else None,
                }
                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()
                if task.estimated_duration_minutes:
                    task_dict["estimated_duration_minutes"] = task.estimated_duration_minutes
                if task.tags:
                    task_dict["tags"] = task.tags
                if task.parent_task_id:
                    task_dict["parent_task_id"] = task.parent_task_id

                task_list.append(task_dict)
            logger.info(f"Returning {len(task_list)} {task_status} status tasks for user {user_id}")
            return {"tasks": task_list}
        except Exception as e:
            logger.error(f"Error in list_tasks_by_status for user {user_id}: {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def list_tasks_by_tags(user_id: str, tags: str) -> Dict[str, Any]:
        """
        Retrieves tasks for the user filtered by tags.

        Parameters:
        - user_id: The ID of the authenticated user
        - tags: The tags to filter by (comma-separated)

        Returns:
        - tasks: Array of task objects [{id, title, completed, description, priority, category, due_date, tags}]
        """
        logger.info(f"list_tasks_by_tags called for user {user_id} with tags: {tags}")

        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            tasks = TaskService.get_tasks_by_tags(session, user_id, tags)
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "description": task.description,
                    "priority": task.priority.value if task.priority else None,
                    "category": task.category.value if task.category else None,
                    "status": task.status.value if task.status else None,
                }
                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()
                if task.estimated_duration_minutes:
                    task_dict["estimated_duration_minutes"] = task.estimated_duration_minutes
                if task.tags:
                    task_dict["tags"] = task.tags
                if task.parent_task_id:
                    task_dict["parent_task_id"] = task.parent_task_id

                task_list.append(task_dict)
            logger.info(f"Returning {len(task_list)} tasks with tags '{tags}' for user {user_id}")
            return {"tasks": task_list}
        except Exception as e:
            logger.error(f"Error in list_tasks_by_tags for user {user_id}: {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def list_overdue_tasks(user_id: str) -> Dict[str, Any]:
        """
        Retrieves overdue tasks for the user.

        Parameters:
        - user_id: The ID of the authenticated user

        Returns:
        - tasks: Array of task objects [{id, title, completed, description, priority, category, due_date}]
        """
        logger.info(f"list_overdue_tasks called for user {user_id}")

        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            tasks = TaskService.get_overdue_tasks(session, user_id)
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "description": task.description,
                    "priority": task.priority.value if task.priority else None,
                    "category": task.category.value if task.category else None,
                    "status": task.status.value if task.status else None,
                }
                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()
                if task.estimated_duration_minutes:
                    task_dict["estimated_duration_minutes"] = task.estimated_duration_minutes
                if task.tags:
                    task_dict["tags"] = task.tags
                if task.parent_task_id:
                    task_dict["parent_task_id"] = task.parent_task_id

                task_list.append(task_dict)
            logger.info(f"Returning {len(task_list)} overdue tasks for user {user_id}")
            return {"tasks": task_list}
        except Exception as e:
            logger.error(f"Error in list_overdue_tasks for user {user_id}: {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def complete_task(user_id: str, task_id: int) -> Dict[str, Any]:
        """
        Marks a task as complete.

        Parameters:
        - user_id: The ID of the authenticated user
        - task_id: The ID of the task to complete

        Returns:
        - task_id: The ID of the completed task
        - status: The status of the task (completed)
        - title: The title of the task
        """
        logger.info(f"complete_task called for user {user_id}, task ID: {task_id}")

        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            task = TaskService.complete_task(session, task_id, user_id)
            if task:
                result = {
                    "task_id": task.id,
                    "status": "completed",
                    "title": task.title
                }
                logger.info(f"Task {task_id} marked as complete for user {user_id}")
                return result
            else:
                error_msg = f"Task with ID {task_id} not found for user {user_id}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        except Exception as e:
            logger.error(f"Error in complete_task for user {user_id}, task {task_id}: {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def delete_task(user_id: str, task_id: int) -> Dict[str, Any]:
        """
        Removes a task.

        Parameters:
        - user_id: The ID of the authenticated user
        - task_id: The ID of the task to delete

        Returns:
        - task_id: The ID of the deleted task
        - status: The status of the task (deleted)
        - title: The title of the task
        """
        logger.info(f"delete_task called for user {user_id}, task ID: {task_id}")

        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            task = TaskService.get_task(session, task_id, user_id)
            if task and TaskService.delete_task(session, task_id, user_id):
                result = {
                    "task_id": task.id,
                    "status": "deleted",
                    "title": task.title
                }
                logger.info(f"Task {task_id} deleted for user {user_id}")
                return result
            else:
                error_msg = f"Task with ID {task_id} not found for user {user_id}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        except Exception as e:
            logger.error(f"Error in delete_task for user {user_id}, task {task_id}: {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def update_task(user_id: str, task_id: int, title: Optional[str] = None, description: Optional[str] = None,
                    priority: Optional[str] = None, category: Optional[str] = None,
                    due_date: Optional[str] = None, estimated_duration_minutes: Optional[int] = None,
                    tags: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Modifies a task's properties.

        Parameters:
        - user_id: The ID of the authenticated user
        - task_id: The ID of the task to update
        - title: Optional new title
        - description: Optional new description
        - priority: Optional new priority (low|medium|high)
        - category: Optional new category (work|personal|shopping|health|finance|other)
        - due_date: Optional new due date (ISO format string)
        - estimated_duration_minutes: Optional new estimated duration in minutes
        - tags: Optional new tags (comma-separated)
        - status: Optional new status (todo|in_progress|review|done)

        Returns:
        - task_id: The ID of the updated task
        - status: The status of the task (pending|completed)
        - title: The title of the task
        """
        logger.info(f"update_task called for user {user_id}, task ID: {task_id}")

        # Get database session
        session_gen = get_session()
        session: Session = next(session_gen)

        try:
            # Get the current task
            current_task = TaskService.get_task(session, task_id, user_id)
            if not current_task:
                error_msg = f"Task with ID {task_id} not found for user {user_id}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Prepare update data
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if priority is not None:
                update_data["priority"] = priority
            if category is not None:
                update_data["category"] = category
            if due_date is not None:
                from datetime import datetime
                update_data["due_date"] = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            if estimated_duration_minutes is not None:
                update_data["estimated_duration_minutes"] = estimated_duration_minutes
            if tags is not None:
                update_data["tags"] = tags
            if status is not None:
                update_data["status"] = status

            # Create a TaskBase object with the updates
            updated_task_data = TaskBase(
                title=update_data.get("title", current_task.title),
                description=update_data.get("description", current_task.description),
                completed=current_task.completed,
                user_id=user_id,
                priority=update_data.get("priority", current_task.priority),
                category=update_data.get("category", current_task.category),
                due_date=update_data.get("due_date", current_task.due_date),
                estimated_duration_minutes=update_data.get("estimated_duration_minutes", current_task.estimated_duration_minutes),
                tags=update_data.get("tags", current_task.tags),
                status=update_data.get("status", current_task.status),
                parent_task_id=current_task.parent_task_id  # Preserve parent_task_id
            )

            # Update the task
            updated_task = TaskService.update_task(session, task_id, user_id, updated_task_data)

            result = {
                "task_id": updated_task.id,
                "status": "completed" if updated_task.completed else "pending",
                "title": updated_task.title
            }
            logger.info(f"Task {task_id} updated for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error in update_task for user {user_id}, task {task_id}: {str(e)}")
            raise
        finally:
            session.close()