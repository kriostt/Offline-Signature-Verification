import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from tensorflow.keras.models import load_model # type: ignore

# Load your trained model (adjust the path)
model = load_model("C:/Users/krisa/Desktop/CPRO 2902/Offline-Signature-Verification/verification_model.h5")

def preprocess_image(image_path):
    image = cv2.imread(image_path)

    # Check if the image is grayscale and convert to RGB if necessary
    if image.shape[-1] == 1:  # Check if the image is grayscale
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)  # Convert to RGB
        
    image = cv2.resize(image, (224, 224))  # Resize to match model input
    image = image.astype('float32') / 255.0  # Normalize
    return np.expand_dims(image, axis=0)  # Add batch dimension

def compare_signatures():
    file_path1 = filedialog.askopenfilename(title="Select Signature 1")
    file_path2 = filedialog.askopenfilename(title="Select Signature 2")
    
    if file_path1 and file_path2:
        # Preprocess images
        signature1 = preprocess_image(file_path1)
        signature2 = preprocess_image(file_path2)

        # Predict similarity using the model
        similarity_score = model.predict([signature1, signature2])
        
        # Assuming a threshold for classification
        threshold = 0.5  # Adjust based on your model's output
        if similarity_score[0][0] > threshold:
            result = "Genuine"
        else:
            result = "Forged"
        
        messagebox.showinfo("Result", f"Similarity Score: {similarity_score[0][0]:.2f}\n"
                                        f"Result: {result}")

# Create the main window with larger dimensions
root = tk.Tk()
root.title("Offline Signature Verification")
root.geometry("500x300")  # Set the size of the window

# Create Compare Button with larger size
compare_btn = tk.Button(root, text="Compare Signatures", command=compare_signatures, height=2, width=20)
compare_btn.pack(pady=50)  # Increase padding for aesthetics

root.mainloop()
