from sqlmodel import Session
from backend.src.database import engine
from backend.src.models import User
from passlib.context import CryptContext
import uuid

# Create password hasher
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Create a test user
test_user = User(
    id='eb47925b-6507-466d-9a22-6057f6993734',
    email='test@example.com',
    password_hash=pwd_context.hash('password123'),
    name='Test User',
    email_verified=True
)

session = Session(engine)
try:
    session.add(test_user)
    session.commit()
    print('Test user created successfully')
    session.refresh(test_user)
    print(f'User details: {test_user.id}, {test_user.email}')
except Exception as e:
    print(f'Error creating test user: {e}')
    session.rollback()
finally:
    session.close()