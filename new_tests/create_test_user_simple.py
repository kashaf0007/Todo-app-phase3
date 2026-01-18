"""
Script to create a test user in the SQLite database
"""
import sys
import os
from sqlmodel import Session, create_engine
from backend.src.models import User

# Explicitly set the database URL to use SQLite
os.environ["DATABASE_URL"] = "sqlite:///./todo_app.db"

# Import after setting the environment variable
from backend.src.database import DATABASE_URL
engine = create_engine(DATABASE_URL, echo=True)

# Create a test user with a simple password hash
# Using a pre-computed bcrypt hash for 'password123'
test_user = User(
    id='eb47925b-6507-466d-9a22-6057f6993734',
    email='test@example.com',
    password_hash='$2b$12$3Gp9JYPqzO6LHHXRwE/HbedQ.HLVu5qzf6Qkv9.fev.UF.9ZKoX4S'  # Hash for 'password123'
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