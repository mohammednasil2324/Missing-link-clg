import sqlite3
import os
import hashlib

DB_PATH = "data/missing_link.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # Missing children table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS missing_children (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        location TEXT NOT NULL,
        date_missing TEXT NOT NULL,
        guardian_contact TEXT NOT NULL,
        photo_path TEXT NOT NULL,
        face_encoding BLOB
    )
    ''')
    
    # Matches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        child_id INTEGER,
        found_photo_path TEXT,
        confidence REAL,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (child_id) REFERENCES missing_children (id)
    )
    ''')
    
    # Alerts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0,
        FOREIGN KEY (match_id) REFERENCES matches (id)
    )
    ''')

    # Add dummy admin if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                       ('admin', admin_pass, 'Admin'))
        
    # Add dummy NGO if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'ngo'")
    if not cursor.fetchone():
        ngo_pass = hashlib.sha256("ngo123".encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                       ('ngo', ngo_pass, 'NGO/Police'))

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    init_db()
    print("Database initialized.")
