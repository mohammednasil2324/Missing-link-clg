import hashlib
import sqlite3
import os
import jwt
from datetime import datetime, timedelta
from database import get_db_connection

JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-missing-link-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        decoded_data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_data
    except Exception:
        return None

def login_user(username, password):
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, pwd_hash)).fetchone()
    conn.close()
    if user:
        return {"id": user['id'], "username": user['username'], "role": user['role']}
    return None

def register_new_user(username, password, role):
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, pwd_hash, role))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success
