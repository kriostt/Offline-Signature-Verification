from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, Frame, Canvas
from tkinter.ttk import Combobox
from PIL import Image, ImageTk
import re
from db_manager import add_user, get_users, add_signature, get_signatures
from signature_utils import preprocess_image, compare_signatures
from tensorflow.keras.models import load_model
from tkinter import font

# Load the trained model
try:
    model = load_model('signature_similarity_model.h5')
    model_status = "Model loaded successfully."
except Exception as e:
    model = None
    model_status = f"Failed to load model: {e}"

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

def update_status(message):
    # Update the status bar message
    status_bar.config(text=message)
    status_bar.update_idletasks()

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
        update_status("User added successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not add user: {e}")
        update_status("Failed to add user.")

def handle_browse_files(entry_widget, preview_canvas, single_file=False):
    # Handle the file browsing functionality
    if single_file:
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, file_path)
            preview_image(file_path, preview_canvas)
    else:
        file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_paths:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, ", ".join(file_paths))

def preview_image(file_path, canvas):
    # Load and display an image in the canvas
    try:
        img = Image.open(file_path)
        img.thumbnail((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        canvas.image = img_tk
        canvas.create_image(100, 100, image=img_tk)
    except Exception as e:
        update_status(f"Error loading image: {e}")

def handle_upload_signatures():
    # Handle uploading signatures
    selected_user = user_combobox.get()
    if not selected_user:
        messagebox.showwarning("Input Error", "Please select a user!")
        return

    file_paths = file_entry.get().split(", ")
    if not file_paths or file_paths == ['']:
        messagebox.showwarning("Input Error", "Please select signature file(s)!")
        return

    user_id = selected_user.split(" - ")[0]

    try:
        for file_path in file_paths:
            with open(file_path, "rb") as file:
                image_data = file.read()
                add_signature(user_id, image_data)
        messagebox.showinfo("Success", "Signature(s) uploaded successfully!")
        user_combobox.set('')
        file_entry.delete(0, 'end')
        update_status("Signatures uploaded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to upload signature: {e}")
        update_status("Failed to upload signatures.")

def handle_verify_signature():
    # Handle verifying a signature
    if model is None:
        messagebox.showerror("Error", "Model not loaded. Cannot verify signature.")
        update_status("Verification failed: Model not loaded.")
        return

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
        # Retrieve stored genuine signatures for the user
        genuine_signatures = get_signatures(user_id)
        if not genuine_signatures:
            messagebox.showerror("Error", "No genuine signatures found for this user.")
            update_status("No genuine signatures found.")
            return

        # Preprocess the uploaded signature and genuine signatures
        input_signature = preprocess_image(file_path)
        input_signature = np.expand_dims(input_signature, axis=0)

        avg_similarity, result = compare_signatures(file_path, genuine_signatures, model)
        messagebox.showinfo("Verification Result", f"Signature {result}! Similarity: {avg_similarity:.2f}")
        update_status(f"Verification result: {result} (Similarity: {avg_similarity:.2f}).")
        verify_user_combobox.set('')
        verify_file_entry.delete(0, 'end')
    except Exception as e:
        messagebox.showerror("Error", f"Could not verify signature: {e}")
        update_status("Verification failed.")

# Tkinter UI
app = Tk()
app.title("Offline Signature Verification System")
app.geometry("600x750")

# Define font styles
label_font = font.Font(family="Times New Roman", size=12, weight="bold")
button_font = font.Font(family="Times New Roman", size=10)

# Add User Section
Label(app, text="Add User", font=label_font).pack(pady=5)
name_entry = Entry(app, width=30)
name_entry.pack(pady=5)
email_entry = Entry(app, width=30)
email_entry.pack(pady=5)
Button(app, text="Add User", command=handle_add_user).pack(pady=10)

# Upload Signatures Section
Label(app, text="Upload Signatures", font=label_font).pack(pady=5)
user_combobox = Combobox(app, width=28, state="readonly")
user_combobox.pack(pady=5)
file_entry = Entry(app, width=30)
file_entry.pack(pady=5)
Button(app, text="Browse", command=lambda: handle_browse_files(file_entry, None)).pack(pady=5)
Button(app, text="Upload Signatures", command=handle_upload_signatures).pack(pady=10)

# Verify Signature Section
Label(app, text="Verify Signature", font=label_font).pack(pady=5)
verify_user_combobox = Combobox(app, width=28, state="readonly")
verify_user_combobox.pack(pady=5)
verify_file_entry = Entry(app, width=30)
verify_file_entry.pack(pady=5)

# Preview Canvas
canvas = Canvas(app, width=200, height=200, bg="white")
canvas.pack(pady=10)
Button(app, text="Browse", command=lambda: handle_browse_files(verify_file_entry, canvas, single_file=True)).pack(pady=5)
Button(app, text="Verify Signature", command=handle_verify_signature).pack(pady=10)

# Status Bar
status_bar = Label(app, text=model_status, bd=1, relief="sunken", anchor="w")
status_bar.pack(side="bottom", fill="x")

# Populate user dropdown
refresh_users()

app.mainloop()