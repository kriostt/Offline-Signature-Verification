import sqlite3
import cv2
import numpy as np
from tkinter import Tk, Label, Button, filedialog, messagebox
from tkinter.ttk import Combobox
from datetime import datetime
from tensorflow.keras.models import load_model  # Adjust this based on your model framework

# Load the trained model
model = load_model("C:/Users/user/Desktop/capstone/verification_model2.h5")  # Replace with your model's path

# Database setup
conn = sqlite3.connect("signature_verification.db")
cursor = conn.cursor()

# Helper Functions


def preprocess_image(image):
    """
    Preprocess image for the model.
    Handles both file paths and numpy arrays.
    """
    if isinstance(image, str):  # If the input is a file path
        img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    else:  # If the input is already a numpy array
        img = image

    img = cv2.resize(img, (224, 224))  # Resize to 224x224
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)  # Convert 1-channel to 3-channel
    img = img / 255.0  # Normalize
    return np.expand_dims(img, axis=0)  # Add batch dimension



def verify_signature():
    selected_user = user_combobox.get()
    if not selected_user:
        messagebox.showwarning("Input Error", "Please select a user!")
        return

    user_id = selected_user.split(" - ")[0]

    # Let the user upload a new signature
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if not file_path:
        return

    try:
        # Preprocess the uploaded signature
        uploaded_signature = preprocess_image(file_path)

        # Retrieve genuine signatures from the database
        cursor.execute("SELECT image_data FROM Signatures WHERE user_id = ?", (user_id,))
        genuine_signatures = cursor.fetchall()
        if not genuine_signatures:
            messagebox.showerror("Error", "No genuine signatures found for this user.")
            return

        # Compare uploaded signature with stored signatures
        similarity_scores = []
        for (image_data,) in genuine_signatures:
            # Convert BLOB to an image
            genuine_image = np.frombuffer(image_data, dtype=np.uint8)
            genuine_image = cv2.imdecode(genuine_image, cv2.IMREAD_GRAYSCALE)
            genuine_image = preprocess_image(genuine_image)

            # Predict similarity (assumes your model outputs a similarity score)
            similarity = model.predict([uploaded_signature, genuine_image])[0][0]
            similarity_scores.append(similarity)

        # Decision based on the highest similarity score
        max_score = max(similarity_scores)
        threshold = 0.5  # Adjust threshold based on your model
        if max_score > threshold:
            messagebox.showinfo("Verification Result", f"Signature Verified! Similarity: {max_score:.2f}")
        else:
            messagebox.showinfo("Verification Result", f"Signature Forged! Similarity: {max_score:.2f}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def refresh_users():
    cursor.execute("SELECT user_id, name FROM Users")
    users = cursor.fetchall()
    user_combobox['values'] = [f"{user[0]} - {user[1]}" for user in users]

# Tkinter UI
app = Tk()
app.title("Signature Verification System")

# Verification Section
Label(app, text="Signature Verification").grid(row=0, column=0, columnspan=2, pady=10)

Label(app, text="Select User:").grid(row=1, column=0, sticky="e")
user_combobox = Combobox(app, width=28, state="readonly")
user_combobox.grid(row=1, column=1)

verify_button = Button(app, text="Verify Signature", command=verify_signature)
verify_button.grid(row=2, column=0, columnspan=2, pady=10)

# Populate users dropdown
refresh_users()

app.mainloop()
