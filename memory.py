import sqlite3
import json
from datetime import datetime

DB_PATH = "memory.db"

def init_db():
    """Creates the database and tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, 
                  role TEXT, 
                  content TEXT)''')
    conn.commit()
    conn.close()

def save_message(role: str, content: str):
    """Saves a single message to the memory."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # If content is a dict/list (like tool calls), convert to JSON string
    if not isinstance(content, str):
        content = json.dumps(content)
        
    c.execute("INSERT INTO history (timestamp, role, content) VALUES (?, ?, ?)",
              (datetime.now().isoformat(), role, content))
    conn.commit()
    conn.close()

def get_recent_memory(limit=10):
    """Retrieves the last N messages to give the agent context."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role, content FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    
    # Reverse so the oldest of the recent messages comes first
    return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

# Initialize DB on import
init_db()