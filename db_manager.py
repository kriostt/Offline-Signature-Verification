import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect("signature_verification2.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Signatures (
    signature_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    image_data BLOB NOT NULL,
    upload_date DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)""")

conn.commit()

# Functions for database operations
def add_user(name, email):
    # Add a new user to the database
    cursor.execute("INSERT INTO Users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()

def get_users():
    # Fetch all users from the database
    cursor.execute("SELECT user_id, name FROM Users")
    return cursor.fetchall()

def add_signature(user_id, image_data):
    # Add a new signature to the database
    cursor.execute("INSERT INTO Signatures (user_id, image_data, upload_date) VALUES (?, ?, ?)", 
                   (user_id, image_data, datetime.now()))
    conn.commit()

def get_signatures(user_id):
    # Fetch all signatures for a specific user
    cursor.execute("SELECT image_data FROM Signatures WHERE user_id = ?", (user_id,))
    return cursor.fetchall()
