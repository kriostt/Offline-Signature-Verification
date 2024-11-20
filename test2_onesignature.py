import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from tensorflow.keras.models import load_model  # type: ignore
import os

# Load the trained model (adjust the path)
model = load_model("C:/Users/krisa/Desktop/CPRO 2902/Offline-Signature-Verification/verification_model.h5")

# Define a threshold for similarity (adjust based on model performance)
THRESHOLD = 0.5  # Genuine if similarity score > threshold

# Preprocess image
def preprocess_image(image_path):
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Failed to load image at {image_path}")
        return np.array([])  # Return empty array if image cannot be loaded

    # Check if the image is grayscale and convert to RGB if necessary
    if image.shape[-1] == 1:  # Check if the image is grayscale
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)  # Convert to RGB
        
    image = cv2.resize(image, (224, 224))  # Resize to match model input
    image = image.astype('float32') / 255.0  # Normalize
    return np.expand_dims(image, axis=0)  # Add batch dimension

# Load the signature database
def load_signature_database(database_folder):
    signatures = []
    labels = []
    
    if not os.path.exists(database_folder):
        print("Error: Database folder does not exist.")
        return signatures, labels

    # Walk through the database folder and load images from subfolders
    for root, dirs, files in os.walk(database_folder):
        for filename in files:
            if filename.endswith(".jpg") or filename.endswith(".png"):  # Support image formats
                file_path = os.path.join(root, filename)
                signature = preprocess_image(file_path)
                if signature.size != 0:
                    signatures.append(signature)
                    # Use the folder name as the label (this assumes each folder corresponds to a user)
                    label = os.path.basename(root)  # Folder name as the label
                    labels.append(label)

    return np.array(signatures), labels

# Compare the input signature to the database
def compare_signatures(input_signature_path):
    if input_signature_path:
        # Preprocess the input signature
        input_signature = preprocess_image(input_signature_path)

        if input_signature.size == 0:
            messagebox.showerror("Error", "Failed to load input signature.")
            return

        # Get the database of genuine signatures
        database_folder = "C:/Users/krisa/Desktop/CPRO 2902/signature_dataset2_after16/genuine"  # Adjust path to your database folder
        database_signatures, labels = load_signature_database(database_folder)

        if len(database_signatures) == 0:
            messagebox.showerror("Error", "No signatures found in the database.")
            return

        # Predict the similarity scores for each signature in the database
        similarity_scores = []
        for signature in database_signatures:
            similarity_score = model.predict([input_signature, signature])
            similarity_scores.append(similarity_score[0][0])

        # Find the most similar signature
        most_similar_index = np.argmax(similarity_scores)
        most_similar_score = similarity_scores[most_similar_index]
        most_similar_label = labels[most_similar_index]

        # Determine if the input signature is genuine or forged
        if most_similar_score > THRESHOLD:
            result = (f"The signature is **genuine**, matching {most_similar_label} "
                      f"with a similarity score of {most_similar_score:.2f}.")
        else:
            result = (f"The signature is **forged**, with no sufficient match found.\n"
                      f"The highest similarity score was {most_similar_score:.2f}.")

        # Display the result
        messagebox.showinfo("Result", result)

# Browse button callback to load the input signature and update the display field
def browse_signature():
    file_path = filedialog.askopenfilename(title="Select Signature", filetypes=[("Image Files", "*.jpg;*.png")])
    
    if file_path:
        # Update the path display field with the selected file path
        input_signature_path_var.set(file_path)

# Create the main window with larger dimensions
root = tk.Tk()
root.title("Offline Signature Verification")
root.geometry("500x400")  # Set the size of the window

# Label for instructions or title
label = tk.Label(root, text="Select a Signature to Compare", font=("Arial", 14))
label.pack(pady=10)

# Browse Button
browse_btn = tk.Button(root, text="Browse", command=browse_signature, height=2, width=20)
browse_btn.pack(pady=10)

# Entry field to show the selected signature path
input_signature_path_var = tk.StringVar()  # To store the path as a string
path_entry = tk.Entry(root, textvariable=input_signature_path_var, width=40, font=("Arial", 12))
path_entry.pack(pady=10)

# Compare Button with larger size
compare_btn = tk.Button(root, text="Verify Signature", command=lambda: compare_signatures(input_signature_path_var.get()), height=2, width=20)
compare_btn.pack(pady=30)  # Increase padding for aesthetics

root.mainloop()
