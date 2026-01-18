import os
from sqlmodel import Session, select
from backend.src.database import engine
from backend.src.models import User

# Make sure we're using the SQLite database
os.environ["DATABASE_URL"] = "sqlite:///./todo_app.db"

# Reload the database module to pick up the new environment variable
import importlib
import backend.src.database
importlib.reload(backend.src.database)
from backend.src.database import engine

# Create a session
session = Session(engine)

# Query for the test user
statement = select(User).where(User.id == "eb47925b-6507-466d-9a22-6057f6993734")
result = session.exec(statement)
user = result.first()

if user:
    print(f"User found: {user.id}, {user.email}")
else:
    print("User not found in database")

session.close()