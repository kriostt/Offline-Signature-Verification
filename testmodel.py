import numpy as np
import cv2
import os
from tensorflow.keras.models import load_model

# Function to load and preprocess an image
def load_and_preprocess_image(path):
    image = cv2.imread(path)
    if image is not None:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, (224, 224))
        image = image / 255.0  # Normalize
        image = image.reshape(224, 224, 1)  # Add the channel dimension
        return image
    else:
        return None

# Load the saved model
model_path = '/Users/alessandrahenriz/Desktop/capstone/signature_verification_model2.keras'
model = load_model(model_path)

# Specify the path to the test folder containing the images
test_folder_path = '/Users/alessandrahenriz/Desktop/capstone/sign_dataset/test/'  
results = []

# Loop through all images in the test folder
for root, _, files in os.walk(test_folder_path):
    for f in files:
        test_image_path = os.path.join(root, f)

        # Load and preprocess the test image
        test_image = load_and_preprocess_image(test_image_path)

        if test_image is not None:
            # Expand dimensions to match the model's input shape (batch size, 224, 224, 1)
            test_image = np.expand_dims(test_image, axis=0)

            # Make predictions using the loaded model
            prediction = model.predict(test_image)

            # Output the prediction
            predicted_label = np.argmax(prediction, axis=1)
            if predicted_label == 0:
                results.append((test_image_path, "Genuine"))
            else:
                results.append((test_image_path, "Forged"))
        else:
            print(f"Error loading the image: {test_image_path}")

# Print the results
for image_path, label in results:
    print(f'Image: {image_path} - Prediction: {label}')
