from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, Frame
from tkinter.ttk import Combobox
import re
from db_manager import add_user, get_users, add_signature, get_signatures
from signature_utils import preprocess_image, verify_signature

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

def handle_browse_files(entry_widget, single_file=False):
    # Handle the file browsing functionality
    if single_file:
        # For signature verification, allow only a single file to be selected
        file_paths = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_paths:  # Check if a file is selected
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, file_paths)  # Only display the single file path
    else:
        # For signature uploading, allow multiple files to be selected
        file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_paths:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, ", ".join(file_paths))  # Display multiple paths as comma-separated

def handle_upload_signatures():
    # Handle uploading signatures
    selected_user = user_combobox.get()
    if not selected_user:
        messagebox.showwarning("Input Error", "Please select a user!")
        return

    file_paths = file_entry.get().split(", ")  # Get file paths from the entry (comma-separated)
    if not file_paths or file_paths == ['']:
        messagebox.showwarning("Input Error", "Please select signature files!")
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

    file_path = verify_file_entry.get()
    if not file_path:
        messagebox.showwarning("Input Error", "Please select a signature file!")
        return

    user_id = selected_user.split(" - ")[0]
    try:
        uploaded_signature = preprocess_image(file_path)  # Preprocess the uploaded signature
        genuine_signatures = [row[0] for row in get_signatures(user_id)]

        if not genuine_signatures:
            messagebox.showerror("Error", "No genuine signatures found for this user.")
            return

        # Verify signature against stored genuine signatures
        max_score, is_verified = verify_signature(uploaded_signature, genuine_signatures)
        result = "Verified" if is_verified else "Forged"
        messagebox.showinfo("Verification Result", f"Signature {result}! Similarity: {max_score:.2f}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not verify signature: {e}")

# Tkinter UI
app = Tk()
app.title("Offline Signature Verification System")
app.geometry("600x400")

# Add User Section
add_user_frame = Frame(app)
add_user_frame.pack(pady=10)
Label(add_user_frame, text="Add User").grid(row=0, column=0, columnspan=3, pady=5)
Label(add_user_frame, text="Name:").grid(row=1, column=0, sticky="e")
name_entry = Entry(add_user_frame, width=30)
name_entry.grid(row=1, column=1)
Label(add_user_frame, text="Email:").grid(row=2, column=0, sticky="e")
email_entry = Entry(add_user_frame, width=30)
email_entry.grid(row=2, column=1)
add_user_button = Button(add_user_frame, text="Add User", command=handle_add_user)
add_user_button.grid(row=3, column=0, columnspan=3, pady=5)

# Upload Signature Section
upload_signature_frame = Frame(app)
upload_signature_frame.pack(pady=10)
Label(upload_signature_frame, text="Upload Signatures").grid(row=0, column=0, columnspan=3, pady=5)
Label(upload_signature_frame, text="Select User:").grid(row=1, column=0, sticky="e")
user_combobox = Combobox(upload_signature_frame, width=28, state="readonly")
user_combobox.grid(row=1, column=1)
Label(upload_signature_frame, text="Signature Files:").grid(row=2, column=0, sticky="e")
file_entry = Entry(upload_signature_frame, width=30)
file_entry.grid(row=2, column=1)
browse_button = Button(upload_signature_frame, text="Browse", command=lambda: handle_browse_files(file_entry, single_file=False))
browse_button.grid(row=2, column=2, padx=(10, 0))  # Added horizontal padding to separate button
upload_signatures_button = Button(upload_signature_frame, text="Upload Signatures", command=handle_upload_signatures)
upload_signatures_button.grid(row=3, column=0, columnspan=3, pady=5)

# Verify Signature Section
verify_signature_frame = Frame(app)
verify_signature_frame.pack(pady=10)
Label(verify_signature_frame, text="Verify Signature").grid(row=0, column=0, columnspan=3, pady=5)
Label(verify_signature_frame, text="Signature File:").grid(row=1, column=0, sticky="e")
verify_file_entry = Entry(verify_signature_frame, width=30)
verify_file_entry.grid(row=1, column=1)
verify_browse_button = Button(verify_signature_frame, text="Browse", command=lambda: handle_browse_files(verify_file_entry, single_file=True))
verify_browse_button.grid(row=1, column=2, padx=(10, 0))  # Added horizontal padding to separate button
verify_button = Button(verify_signature_frame, text="Verify Signature", command=handle_verify_signature)
verify_button.grid(row=2, column=0, columnspan=3, pady=5)

# Populate user dropdown
refresh_users()

app.mainloop()
