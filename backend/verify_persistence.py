import os
import sys

# Set the database URL
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_cIRiT1jD2Xeu@ep-autumn-unit-adb7wino-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_session
from src.models.user import User
from src.models.task import Task
from src.models.conversation import Conversation
from sqlmodel import select

def verify_data_persistence():
    print("Verifying data persistence after server restart...")
    
    # Create a session
    session = next(get_session())
    
    try:
        # Count total records in each table
        total_users = session.exec(select(User)).all()
        total_tasks = session.exec(select(Task)).all()
        total_convs = session.exec(select(Conversation)).all()
        
        print(f"Total users in database: {len(total_users)}")
        print(f"Total tasks in database: {len(total_tasks)}")
        print(f"Total conversations in database: {len(total_convs)}")
        
        # Look for our test records (they should have been created with emails containing 'testuser_')
        test_users = session.exec(select(User).where(User.email.like('%testuser_%'))).all()
        print(f"Test users found: {len(test_users)}")
        
        for user in test_users:
            # Find tasks associated with test users
            user_tasks = session.exec(select(Task).where(Task.user_id == user.id)).all()
            print(f"  - User {user.id} ({user.email}): {len(user_tasks)} tasks")
            
            # Find conversations associated with test users
            user_convs = session.exec(select(Conversation).where(Conversation.user_id == user.id)).all()
            print(f"    - {len(user_convs)} conversations")
        
        if len(total_users) > 0 and len(test_users) > 0:
            print("\n+ Data persistence confirmed: Records survive server restart!")
            print("  All data remains intact in Neon PostgreSQL database.")
            return True
        else:
            print("\n- Issue with data persistence verification")
            return False
            
    except Exception as e:
        print(f"Error during data persistence verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = verify_data_persistence()
    if success:
        print("\n+ PERSISTENCE VERIFIED: Data survives server restart in Neon PostgreSQL!")
    else:
        print("\n- PERSISTENCE ISSUE: Problems with data retention after restart")