import sqlite3

# Define database file name
db_file = "database.db"

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect(db_file)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create a sample table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        age INTEGER
    )
''')

# Insert sample data
users = [
    ("Alice", "alice@example.com", 25),
    ("Bob", "bob@example.com", 30),
    ("Charlie", "charlie@example.com", 28),
]

cursor.executemany("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", users)

# Commit changes and close connection
conn.commit()
conn.close()

print(f"Database '{db_file}' created successfully with sample data.")
