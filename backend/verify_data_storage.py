import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

# Set the database URL
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_cIRiT1jD2Xeu@ep-autumn-unit-adb7wino-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_session
from src.models.user import User
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message
from sqlmodel import select

def test_data_storage():
    print("Starting data storage verification...")

    # Create a session
    session = next(get_session())

    try:
        # Count existing users before insertion
        existing_users = session.exec(select(User)).all()
        print(f"Existing users in database: {len(existing_users)}")

        # Create a test user with unique email
        import uuid
        unique_email = f'testuser_{uuid.uuid4()}@example.com'
        test_user = User(
            id=str(uuid4()),
            email=unique_email,
            password_hash='$2b$12$dummy_hash_for_testing_purposes_only',
            created_at=datetime.now(timezone.utc)
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)
        print(f"Test user created with ID: {test_user.id}")

        # Create a test task for the user
        test_task = Task(
            title='Test Task',
            description='This is a test task to verify database storage',
            user_id=test_user.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        session.add(test_task)
        session.commit()
        session.refresh(test_task)
        print(f"Test task created with ID: {test_task.id}")

        # Create a test conversation for the user
        test_conv = Conversation(
            user_id=test_user.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        session.add(test_conv)
        session.commit()
        session.refresh(test_conv)
        print(f"Test conversation created with ID: {test_conv.id}")

        # Create a test message in the conversation
        test_message = Message(
            user_id=test_user.id,
            conversation_id=test_conv.id,
            role='user',
            content='This is a test message to verify database storage',
            created_at=datetime.now(timezone.utc)
        )
        session.add(test_message)
        session.commit()
        session.refresh(test_message)
        print(f"Test message created with ID: {test_message.id}")

        # Verify all records exist by querying them back
        retrieved_user = session.exec(select(User).where(User.id == test_user.id)).first()
        retrieved_task = session.exec(select(Task).where(Task.id == test_task.id)).first()
        retrieved_conv = session.exec(select(Conversation).where(Conversation.id == test_conv.id)).first()
        retrieved_msg = session.exec(select(Message).where(Message.id == test_message.id)).first()

        print("\nVerification results:")
        print(f"User exists: {retrieved_user is not None}")
        print(f"Task exists: {retrieved_task is not None}")
        print(f"Conversation exists: {retrieved_conv is not None}")
        print(f"Message exists: {retrieved_msg is not None}")

        if all([retrieved_user, retrieved_task, retrieved_conv, retrieved_msg]):
            print("\n✓ All test records successfully stored and retrieved from Neon DB!")
            return True
        else:
            print("\n✗ Some records were not properly stored/retrieved")
            return False

    except Exception as e:
        print(f"Error during data storage verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = test_data_storage()
    if success:
        print("\n✓ VERIFICATION COMPLETE: All data is being stored in Neon PostgreSQL!")
    else:
        print("\n✗ VERIFICATION FAILED: Issues with data storage in Neon DB")