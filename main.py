from tkinter import Tk, Label, Entry, Button, filedialog, messagebox
from tkinter.ttk import Combobox
import re
from db_manager import add_user, get_users, add_signature, get_signatures
from image_utils import preprocess_image, verify_signature

# Helper Functions
def is_valid_email(email):
    # Validate email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def refresh_users():
    # Refresh the user list in the combobox
    users = get_users()
    user_combobox['values'] = [f"{user[0]} - {user[1]}" for user in users]

def handle_add_user():
    # Handle adding a new user
    name = name_entry.get()
    email = email_entry.get()
    
    if not name or not email:
        messagebox.showwarning("Input Error", "Name and email are required!")
        return

    if not is_valid_email(email):
        messagebox.showwarning("Invalid Email", "Please enter a valid email address!")
        return

    try:
        add_user(name, email)
        messagebox.showinfo("Success", "User added successfully!")
        name_entry.delete(0, 'end')
        email_entry.delete(0, 'end')
        refresh_users()
    except Exception as e:
        messagebox.showerror("Error", f"Could not add user: {e}")

def handle_upload_signatures():
    # Handle uploading signatures
    selected_user = user_combobox.get()
    if not selected_user:
        messagebox.showwarning("Input Error", "Please select a user!")
        return

    file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if not file_paths:
        return

    user_id = selected_user.split(" - ")[0]
    for file_path in file_paths:
        try:
            with open(file_path, "rb") as file:
                add_signature(user_id, file.read())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload a signature: {e}")
    messagebox.showinfo("Success", "Signatures uploaded successfully!")

def handle_verify_signature():
    # Handle verifying a signature
    selected_user = user_combobox.get()
    if not selected_user:
        messagebox.showwarning("Input Error", "Please select a user!")
        return

    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if not file_path:
        return

    user_id = selected_user.split(" - ")[0]
    try:
        uploaded_signature = preprocess_image(file_path)
        genuine_signatures = [row[0] for row in get_signatures(user_id)]

        if not genuine_signatures:
            messagebox.showerror("Error", "No genuine signatures found for this user.")
            return

        max_score, is_verified = verify_signature(uploaded_signature, genuine_signatures)
        result = "Verified" if is_verified else "Forged"
        messagebox.showinfo("Verification Result", f"Signature {result}! Similarity: {max_score:.2f}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not verify signature: {e}")

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
add_user_button = Button(app, text="Add User", command=handle_add_user)
add_user_button.grid(row=3, column=0, columnspan=2, pady=10)

# Upload Signature Section
Label(app, text="Upload Signatures").grid(row=4, column=0, columnspan=2, pady=10)
Label(app, text="Select User:").grid(row=5, column=0, sticky="e")
user_combobox = Combobox(app, width=28, state="readonly")
user_combobox.grid(row=5, column=1)
upload_signatures_button = Button(app, text="Upload Signatures", command=handle_upload_signatures)
upload_signatures_button.grid(row=6, column=0, columnspan=2, pady=10)

# Verify Signature Section
Label(app, text="Verify Signature").grid(row=7, column=0, columnspan=2, pady=10)
verify_button = Button(app, text="Verify Signature", command=handle_verify_signature)
verify_button.grid(row=8, column=0, columnspan=2, pady=10)

# Populate user dropdown
refresh_users()

app.mainloop()
