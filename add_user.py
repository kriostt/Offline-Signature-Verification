import sqlite3
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox
from tkinter.ttk import Combobox
from datetime import datetime
import re

# Database setup
conn = sqlite3.connect("signature_verification.db")
cursor = conn.cursor()

# Create tables
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

# Functions for UI
# Function to validate email format
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def add_user():
    name = name_entry.get()
    email = email_entry.get()
    
    if not name or not email:
        messagebox.showwarning("Input Error", "Name and email are required!")
        return
    
    # Validate email format
    if not is_valid_email(email):
        messagebox.showwarning("Invalid Email", "Please enter a valid email address!")
        return
    
    try:
        cursor.execute("INSERT INTO Users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        messagebox.showinfo("Success", "User added successfully!")
        name_entry.delete(0, 'end')
        email_entry.delete(0, 'end')
        refresh_users()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Email already exists!")

def upload_signature():
    selected_user = user_combobox.get()
    if not selected_user:
        messagebox.showwarning("Input Error", "Please select a user!")
        return
    
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if not file_path:
        return
    
    try:
        with open(file_path, "rb") as file:
            image_data = file.read()
        
        user_id = user_combobox.get().split(" - ")[0]
        upload_date = datetime.now()
        cursor.execute("INSERT INTO Signatures (user_id, image_data, upload_date) VALUES (?, ?, ?)", 
                       (user_id, image_data, upload_date))
        conn.commit()
        messagebox.showinfo("Success", "Signature uploaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def refresh_users():
    cursor.execute("SELECT user_id, name FROM Users")
    users = cursor.fetchall()
    user_combobox['values'] = [f"{user[0]} - {user[1]}" for user in users]

# Tkinter UI
app = Tk()
app.title("Offline Signature Verification System")

# Add User Section
Label(app, text="Add User").grid(row=0, column=0, columnspan=2, pady=10)

Label(app, text="Name:").grid(row=1, column=0, sticky="e")
name_entry = Entry(app, width=30)
name_entry.grid(row=1, column=1)

Label(app, text="Email:").grid(row=2, column=0, sticky="e")
email_entry = Entry(app, width=30)
email_entry.grid(row=2, column=1)

add_user_button = Button(app, text="Add User", command=add_user)
add_user_button.grid(row=3, column=0, columnspan=2, pady=10)

# Upload Signature Section
Label(app, text="Upload Signature").grid(row=4, column=0, columnspan=2, pady=10)

Label(app, text="Select User:").grid(row=5, column=0, sticky="e")
user_combobox = Combobox(app, width=28, state="readonly")
user_combobox.grid(row=5, column=1)

upload_signature_button = Button(app, text="Upload Signature", command=upload_signature)
upload_signature_button.grid(row=6, column=0, columnspan=2, pady=10)

# Populate users dropdown
refresh_users()

app.mainloop()
