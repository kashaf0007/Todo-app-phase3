import sqlite3

# Connect to the database
conn = sqlite3.connect('todo_app.db')
cursor = conn.cursor()

# Query for the user
cursor.execute("SELECT id, email FROM users WHERE id = ?", ("eb47925b-6507-466d-9a22-6057f6993734",))
result = cursor.fetchone()

if result:
    print(f"User found: {result[0]}, {result[1]}")
else:
    print("User not found in database")

# Close the connection
conn.close()