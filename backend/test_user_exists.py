from src.database import get_session
from src.models import User, Task
from sqlmodel import select
from uuid import UUID

def test_user_exists():
    session_gen = get_session()
    session = next(session_gen)

    try:
        # Check if the user exists in the database
        user_id = "eb47925b-6507-466d-9a22-6057f6993734"

        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()

        if user:
            print(f"User {user_id} exists in the database:")
            print(f"  ID: {user.id}")
            print(f"  Email: {user.email}")
            # Note: User model might not have a 'name' attribute
        else:
            print(f"User {user_id} does not exist in the database")

            # List all users to see what's available
            all_users = session.exec(select(User)).all()
            if all_users:
                print("\nAvailable users in the database:")
                for u in all_users:
                    print(f"  - ID: {u.id}, Email: {u.email}")
            else:
                print("\nNo users found in the database")

        # Also check if the user has any tasks
        task_statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(task_statement).all()

        print(f"\nUser {user_id} has {len(tasks)} tasks:")
        for i, task in enumerate(tasks):
            print(f"  {i+1}. ID: {task.id}, Title: {task.title}, Completed: {task.completed}")

    except Exception as e:
        print(f"Error checking user: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    test_user_exists()