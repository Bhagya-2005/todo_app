import sqlite3

# Connect to database (creates file if it doesn't exist)
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create tasks table
c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT
)
''')

conn.commit()
conn.close()

print("Database initialized successfully.")
