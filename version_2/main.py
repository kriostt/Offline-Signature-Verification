from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, Frame
from tkinter.ttk import Combobox
import re
from db_manager import add_user, get_users, add_signature, get_signatures
from signature_utils import preprocess_image, verify_signature
from tkinter import font
from tensorflow.keras.models import load_model

# Load the trained model
model = load_model("C:/Users/krisa/Desktop/CPRO 2902/Offline-Signature-Verification/version_2/signature_similarity_model.h5")

# Helper Functions
def is_valid_email(email):
    # Validate email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def refresh_users():
    # Refresh the user list in the combobox
    users = get_users()
    user_combobox['values'] = [f"{user[0]} - {user[1]}" for user in users]
    verify_user_combobox['values'] = [f"{user[0]} - {user[1]}" for user in users]

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
        messagebox.showwarning("Input Error", "Please select signature file(s)!")
        return

    user_id = selected_user.split(" - ")[0]

    # Get existing signature BLOBs for the selected user
    existing_signatures = [row[0] for row in get_signatures(user_id)]

    for file_path in file_paths:
        try:
            # Read the image file as binary data (BLOB)
            with open(file_path, "rb") as file:
                image_data = file.read()

            # Check if the signature already exists by comparing BLOBs
            if image_data in existing_signatures:
                response = messagebox.askyesno(
                    "Signature Exists",
                    f"This signature already exists.\nDo you want to replace it?"
                )
                if response:  # If the user selects 'Yes', replace the signature
                    # Replace the existing signature 
                    existing_signatures.remove(image_data)  # Remove the old one
                    add_signature(user_id, image_data)  # Add the new one
                else:
                    continue  # Skip this file if the user chooses not to replace
                
            else:
                # Add the signature if it doesn't exist
                add_signature(user_id, image_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload signature: {e}")
            return

    messagebox.showinfo("Success", "Signature(s) uploaded successfully!")
    user_combobox.set('')
    file_entry.delete(0, 'end')

def handle_verify_signature():
    # Handle verifying a signature
    selected_user = verify_user_combobox.get()
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
        max_score, is_verified = verify_signature(uploaded_signature, genuine_signatures, model)
        result = "Verified" if is_verified else "Forged"
        messagebox.showinfo("Verification Result", f"Signature {result}! Similarity: {max_score:.2f}")
        verify_user_combobox.set('')
        verify_file_entry.delete(0, 'end')
    except Exception as e:
        messagebox.showerror("Error", f"Could not verify signature: {e}")

# Tkinter UI
app = Tk()
app.title("Offline Signature Verification System")
app.geometry("600x630")

# Set background color for the main app window
app.configure(bg="#D2B48C")  # Light gray background

# Create a frame to hold the entire UI with a border around it
outer_frame = Frame(app, bg="#D2B48C", bd=3, relief="solid")  # Border around the entire UI
outer_frame.pack(padx=30, pady=30, fill="both", expand=True)


# Define font styles for labels and buttons
label_font = font.Font(family="Times New Roman", size=12, weight="bold")
button_font = font.Font(family="Times New Roman", size=10)

# Add a Label at the top with italicized text inside the outer frame
title_font = font.Font(family="Times New Roman", size=16, weight="bold", slant="italic")
title_label = Label(
    outer_frame, 
    text="Offline Signature Verification System", 
    font=title_font, 
    bg="#D2B48C",  # Light brown background
    fg="#4E3629",  # Dark brown text
    width=30,  # Set a width for the label
    anchor="center"  # Center the text inside the label
)

title_label.pack(pady=5, anchor="n", padx=5, fill="x") 

# Add User Section
add_user_frame = Frame(outer_frame, bg="#D2B48C")
add_user_frame.pack(pady=10)
Label(add_user_frame, text="Add User", font=label_font, bg="#D2B48C", fg="#4E3629").grid(row=0, column=0, columnspan=3, pady=5)
Label(add_user_frame, text="Name:", font=label_font, bg="#D2B48C", fg="#4E3629").grid(row=1, column=0, sticky="e", pady=5)
name_entry = Entry(add_user_frame, width=30, font=("Times New Roman", 12), relief="solid")
name_entry.grid(row=1, column=1, pady=5)
Label(add_user_frame, text="Email:", font=label_font, bg="#D2B48C", fg="#4E3629").grid(row=2, column=0, sticky="e", pady=5)
email_entry = Entry(add_user_frame, width=30, font=("Times New Roman", 12), relief="solid")
email_entry.grid(row=2, column=1,  pady=5)
add_user_button = Button(add_user_frame, text="Add User", command=handle_add_user, font=button_font, bg="#8B4513", fg="white", relief="raised", bd=2)
add_user_button.grid(row=3, column=0, columnspan=3, pady=10)

# Upload Signature Section
upload_signature_frame = Frame(outer_frame, bg="#D2B48C")
upload_signature_frame.pack(pady=10)
Label(upload_signature_frame, text="Upload Signatures", font=label_font, bg="#D2B48C", fg="#4E3629").grid(row=0, column=0, columnspan=3, pady=5)
Label(upload_signature_frame, text="Select User:", font=label_font, bg="#D2B48C", fg="#4E3629").grid(row=1, column=0, sticky="e", pady=5)
user_combobox = Combobox(upload_signature_frame, width=28, state="readonly",  font=("Times New Roman", 12))
user_combobox.grid(row=1, column=1, pady=5)
Label(upload_signature_frame, text="Signature Files:", font=label_font, bg="#D2B48C", fg="#4E3629").grid(row=2, column=0, sticky="e", pady=5)
file_entry = Entry(upload_signature_frame, width=30, font=("Times New Roman", 12), relief="solid")
file_entry.grid(row=2, column=1, pady=5)
browse_button = Button(upload_signature_frame, text="Browse", command=lambda: handle_browse_files(file_entry, single_file=False), font=button_font, bg="#8B4513", fg="white", relief="raised", bd=2)
browse_button.grid(row=2, column=2, padx=(10, 0))  # Added horizontal padding to separate button
upload_signatures_button = Button(upload_signature_frame, text="Upload Signatures", command=handle_upload_signatures, font=button_font, bg="#8B4513", fg="white", relief="raised", bd=2)
upload_signatures_button.grid(row=3, column=0, columnspan=3, pady=10)

# Verify Signature Section
verify_signature_frame = Frame(outer_frame, bg="#D2B48C")
verify_signature_frame.pack(pady=10)
Label(verify_signature_frame, text="Verify Signature", font=label_font, bg="#D2B48C", fg="#4E3629").grid(row=0, column=0, columnspan=3, pady=5)
Label(verify_signature_frame, text="Select User:", font=label_font, bg="#D2B48C", fg="#4E3629").grid(row=1, column=0, sticky="e", pady=5)
verify_user_combobox = Combobox(verify_signature_frame, width=28, state="readonly",  font=("Times New Roman", 12))
verify_user_combobox.grid(row=1, column=1, pady=5)
Label(verify_signature_frame, text="Signature File:", font=label_font, bg="#D2B48C", fg="#4E3629").grid(row=2, column=0, sticky="e", pady=5)
verify_file_entry = Entry(verify_signature_frame, width=30, font=("Times New Roman", 12), relief="solid")
verify_file_entry.grid(row=2, column=1, pady=5)
verify_browse_button = Button(verify_signature_frame, text="Browse", command=lambda: handle_browse_files(verify_file_entry, single_file=True), font=button_font, bg="#8B4513", fg="white", relief="raised", bd=2)
verify_browse_button.grid(row=2, column=2, padx=(10, 0))  # Added horizontal padding to separate button
verify_button = Button(verify_signature_frame, text="Verify Signature", command=handle_verify_signature, font=button_font, bg="#8B4513", fg="white", relief="raised", bd=2)
verify_button.grid(row=3, column=0, columnspan=3, pady=15)

# Populate user dropdown
refresh_users()

app.mainloop()
