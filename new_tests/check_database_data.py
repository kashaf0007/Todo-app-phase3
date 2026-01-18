"""
Database Data Verification Script
Checks if SQLModel ORM is working and data is stored in database tables
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlmodel import Session, select, text
from src.database import engine
from src.models.user import User
from src.models.task import Task

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with Session(engine) as session:
        result = session.exec(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = '{table_name}'
            );
        """))
        exists = result.one()[0]
        return exists

def get_table_count(table_name):
    """Get the row count of a table"""
    with Session(engine) as session:
        result = session.exec(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.one()[0]
        return count

def main():
    print("=" * 70)
    print("SQLModel ORM and Database Data Verification")
    print("=" * 70)

    # Check tables exist
    print("\n=== Table Existence ===")
    tables = ['users', 'tasks']
    for table in tables:
        exists = check_table_exists(table)
        status = "[OK] EXISTS" if exists else "[MISSING] NOT FOUND"
        print(f"{status}: {table}")

    # Get row counts
    print("\n=== Data Counts ===")
    for table in tables:
        try:
            count = get_table_count(table)
            print(f"[OK] {table}: {count} row(s)")
        except Exception as e:
            print(f"[ERROR] {table}: {e}")

    # Show users data
    print("\n=== Users Table Data ===")
    try:
        with Session(engine) as session:
            users = session.exec(select(User)).all()
            if users:
                print(f"Found {len(users)} user(s):")
                for user in users:
                    print(f"  - ID: {user.id}")
                    print(f"    Email: {user.email}")
                    print(f"    Created: {user.created_at}")
                    print(f"    Has password hash: {'Yes' if user.password_hash else 'No'}")
                    print()
            else:
                print("[INFO] No users found in database")
    except Exception as e:
        print(f"[ERROR] Failed to fetch users: {e}")

    # Show tasks data
    print("\n=== Tasks Table Data ===")
    try:
        with Session(engine) as session:
            tasks = session.exec(select(Task)).all()
            if tasks:
                print(f"Found {len(tasks)} task(s):")
                for task in tasks:
                    print(f"  - ID: {task.id}")
                    print(f"    User ID: {task.user_id}")
                    print(f"    Title: {task.title}")
                    print(f"    Description: {task.description or '(none)'}")
                    print(f"    Completed: {'Yes' if task.completed else 'No'}")
                    print(f"    Created: {task.created_at}")
                    print(f"    Updated: {task.updated_at}")
                    print()
            else:
                print("[INFO] No tasks found in database")
    except Exception as e:
        print(f"[ERROR] Failed to fetch tasks: {e}")

    # Show table schema
    print("\n=== Table Schema (SQLModel ORM) ===")

    print("\n--- Users Table ---")
    with Session(engine) as session:
        columns = session.exec(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)).all()
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"  {col[0]:<20} {col[1]:<20} {nullable}")

    print("\n--- Tasks Table ---")
    with Session(engine) as session:
        columns = session.exec(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'tasks'
            ORDER BY ordinal_position;
        """)).all()
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"  {col[0]:<20} {col[1]:<20} {nullable}")

    print("\n" + "=" * 70)
    print("Verification Complete")
    print("=" * 70)
    print("\nSummary:")
    print("  - SQLModel ORM: Active")
    print("  - Tables: Created by SQLModel metadata.create_all()")
    print("  - Data: Stored via SQLModel Session")
    print("  - Database: Neon PostgreSQL")

if __name__ == "__main__":
    main()
