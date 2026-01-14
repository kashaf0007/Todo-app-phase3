from sqlmodel import Session, select
from typing import List, Optional
from ..models.task import Task, TaskBase, TaskStatus
from datetime import datetime
from ..logging_config import logger


class TaskService:
    @staticmethod
    def create_task(session: Session, task_data: TaskBase) -> Task:
        try:
            # Validate task data
            if not task_data.title or len(task_data.title.strip()) == 0:
                raise ValueError("Task title cannot be empty")

            task = Task.from_orm(task_data) if hasattr(Task, 'from_orm') else Task(**task_data.dict())
            session.add(task)
            session.commit()
            session.refresh(task)
            logger.info(f"Task created with ID: {task.id} for user: {task.user_id}")
            return task
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise

    @staticmethod
    def get_tasks(session: Session, user_id: str, status: Optional[str] = None, priority: Optional[str] = None,
                 category: Optional[str] = None, due_before: Optional[datetime] = None,
                 search_term: Optional[str] = None, task_status: Optional[str] = None,
                 tags: Optional[str] = None, parent_task_id: Optional[int] = None,
                 completed: Optional[bool] = None) -> List[Task]:
        try:
            query = select(Task).where(Task.user_id == user_id)

            # Apply filters based on parameters
            if status:  # Legacy status filter (completed/pending)
                if status == "completed":
                    query = query.where(Task.completed == True)
                elif status == "pending":
                    query = query.where(Task.completed == False)
                elif status != "all":
                    raise ValueError(f"Invalid status: {status}. Expected 'all', 'pending', or 'completed'")

            # Apply new task status filter
            if task_status:
                query = query.where(Task.status == task_status)

            if priority:
                query = query.where(Task.priority == priority)

            if category:
                query = query.where(Task.category == category)

            if due_before:
                query = query.where(Task.due_date <= due_before)

            if search_term:
                # Search in title and description
                search_pattern = f"%{search_term}%"
                query = query.where(
                    (Task.title.ilike(search_pattern)) |
                    (Task.description.ilike(search_pattern) if Task.description is not None else False)
                )

            # Apply new filters
            if tags:
                # Filter by tags (comma-separated)
                tag_list = [tag.strip() for tag in tags.split(',')]
                for tag in tag_list:
                    query = query.where(Task.tags.ilike(f"%{tag}%"))

            if parent_task_id is not None:
                query = query.where(Task.parent_task_id == parent_task_id)

            if completed is not None:
                query = query.where(Task.completed == completed)

            # Order by priority, status, and due date
            query = query.order_by(Task.priority.desc(), Task.status, Task.due_date.asc())

            tasks = session.exec(query).all()
            logger.info(f"Retrieved {len(tasks)} tasks for user: {user_id} with filters applied")
            return tasks
        except Exception as e:
            logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_tasks_by_priority(session: Session, user_id: str, priority: str) -> List[Task]:
        """Get tasks filtered by priority"""
        try:
            query = select(Task).where(
                Task.user_id == user_id,
                Task.priority == priority
            ).order_by(Task.status, Task.due_date.asc())

            tasks = session.exec(query).all()
            logger.info(f"Retrieved {len(tasks)} {priority} priority tasks for user: {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"Error retrieving {priority} priority tasks for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_tasks_by_category(session: Session, user_id: str, category: str) -> List[Task]:
        """Get tasks filtered by category"""
        try:
            query = select(Task).where(
                Task.user_id == user_id,
                Task.category == category
            ).order_by(Task.priority.desc(), Task.status, Task.due_date.asc())

            tasks = session.exec(query).all()
            logger.info(f"Retrieved {len(tasks)} {category} category tasks for user: {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"Error retrieving {category} category tasks for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_overdue_tasks(session: Session, user_id: str) -> List[Task]:
        """Get tasks that are overdue"""
        try:
            from datetime import datetime
            now = datetime.utcnow()
            query = select(Task).where(
                Task.user_id == user_id,
                Task.completed == False,
                Task.due_date.is_not(None),
                Task.due_date < now
            ).order_by(Task.due_date.asc())

            tasks = session.exec(query).all()
            logger.info(f"Retrieved {len(tasks)} overdue tasks for user: {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"Error retrieving overdue tasks for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_task(session: Session, task_id: int, user_id: str) -> Optional[Task]:
        try:
            query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(query).first()
            if task:
                logger.info(f"Retrieved task with ID: {task_id} for user: {user_id}")
            else:
                logger.warning(f"Task with ID {task_id} not found for user: {user_id}")
            return task
        except Exception as e:
            logger.error(f"Error retrieving task {task_id} for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def update_task(session: Session, task_id: int, user_id: str, task_data: TaskBase) -> Optional[Task]:
        try:
            task = TaskService.get_task(session, task_id, user_id)
            if not task:
                raise ValueError(f"Task with ID {task_id} not found for user {user_id}")

            # Apply updates
            for key, value in task_data.dict(exclude_unset=True).items():
                if key != 'id' and key != 'user_id':  # Prevent updating ID or user_id
                    setattr(task, key, value)

            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
            logger.info(f"Task updated with ID: {task_id} for user: {user_id}")
            return task
        except Exception as e:
            logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def delete_task(session: Session, task_id: int, user_id: str) -> bool:
        try:
            task = TaskService.get_task(session, task_id, user_id)
            if not task:
                logger.warning(f"Attempted to delete non-existent task {task_id} for user {user_id}")
                return False

            session.delete(task)
            session.commit()
            logger.info(f"Task deleted with ID: {task_id} for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def complete_task(session: Session, task_id: int, user_id: str) -> Optional[Task]:
        try:
            task = TaskService.get_task(session, task_id, user_id)
            if not task:
                raise ValueError(f"Task with ID {task_id} not found for user {user_id}")

            task.completed = True
            task.status = TaskStatus.DONE  # Update status to done when completed
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
            logger.info(f"Task marked as complete with ID: {task_id} for user: {user_id}")
            return task
        except Exception as e:
            logger.error(f"Error completing task {task_id} for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_tasks_by_status(session: Session, user_id: str, task_status: str) -> List[Task]:
        """Get tasks filtered by the new status field"""
        try:
            query = select(Task).where(
                Task.user_id == user_id,
                Task.status == task_status
            ).order_by(Task.priority.desc(), Task.due_date.asc())

            tasks = session.exec(query).all()
            logger.info(f"Retrieved {len(tasks)} tasks with status '{task_status}' for user: {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"Error retrieving tasks with status '{task_status}' for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_tasks_by_tags(session: Session, user_id: str, tags: str) -> List[Task]:
        """Get tasks filtered by tags (comma-separated)"""
        try:
            tag_list = [tag.strip() for tag in tags.split(',')]
            query = select(Task).where(Task.user_id == user_id)

            # Build OR condition for tags
            tag_conditions = []
            for tag in tag_list:
                tag_conditions.append(Task.tags.ilike(f"%{tag}%"))

            if tag_conditions:
                from sqlalchemy import or_
                query = query.where(or_(*tag_conditions))

            query = query.order_by(Task.priority.desc(), Task.status, Task.due_date.asc())

            tasks = session.exec(query).all()
            logger.info(f"Retrieved {len(tasks)} tasks with tags '{tags}' for user: {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"Error retrieving tasks with tags '{tags}' for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_subtasks(session: Session, user_id: str, parent_task_id: int) -> List[Task]:
        """Get subtasks for a parent task"""
        try:
            query = select(Task).where(
                Task.user_id == user_id,
                Task.parent_task_id == parent_task_id
            ).order_by(Task.position)

            tasks = session.exec(query).all()
            logger.info(f"Retrieved {len(tasks)} subtasks for parent task {parent_task_id} for user: {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"Error retrieving subtasks for parent task {parent_task_id} for user {user_id}: {str(e)}")
            raise