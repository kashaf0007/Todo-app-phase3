"""
Simple script to test authentication and get a valid token
"""
import os
import sqlite3
from datetime import datetime, timedelta
from jose import jwt

# Connect to the SQLite database
conn = sqlite3.connect('todo_app.db')
cursor = conn.cursor()

# Verify the test user exists
cursor.execute("SELECT id FROM users WHERE id = ?", ('eb47925b-6507-466d-9a22-6057f6993734',))
result = cursor.fetchone()

if result:
    print("Test user exists in database")
    
    # Generate a JWT token for the test user
    secret = "your-super-secret-key-for-testing-purposes-only-32chars"
    payload = {
        "sub": "eb47925b-6507-466d-9a22-6057f6993734",  # User ID
        "exp": datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        "iat": datetime.utcnow(),  # Issued at
        "type": "access"  # Token type
    }

    token = jwt.encode(payload, secret, algorithm="HS256")
    print(f"Valid JWT token: {token}")
    print("\nMake sure your frontend sends this token in the Authorization header as 'Bearer {token}'")
else:
    print("Test user does not exist in database")

conn.close()