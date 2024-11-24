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
model_path = "C:/Users/krisa/Desktop/CPRO 2902/Offline-Signature-Verification/signature_verification_model.keras"
model = load_model(model_path)

# Specify the path to the test folder containing the images
test_folder_path = "C:/Users/krisa/Desktop/CPRO 2902/signature_verification_dataset/sign_data/test"
results = []
true_labels = []  # List to store true labels
predictions = []  # List to store predictions

# Loop through all images in the test folder
for root, dirs, files in os.walk(test_folder_path):
    for label in dirs:  # For each subfolder (genuine or forged)
        label_path = os.path.join(root, label)
        for f in os.listdir(label_path):
            test_image_path = os.path.join(label_path, f)

            # Load and preprocess the test image
            test_image = load_and_preprocess_image(test_image_path)

            if test_image is not None:
                # Expand dimensions to match the model's input shape (batch size, 224, 224, 1)
                test_image = np.expand_dims(test_image, axis=0)

                # Make predictions using the loaded model
                prediction = model.predict(test_image)

                # Output the prediction
                predicted_label = np.argmax(prediction, axis=1)[0]
                predictions.append(predicted_label)

                # Add true label (0 for genuine, 1 for forged)
                true_labels.append(0 if label == "genuine" else 1)

                # Store result with prediction
                results.append((test_image_path, "Genuine" if predicted_label == 0 else "Forged"))
            else:
                print(f"Error loading the image: {test_image_path}")

# Calculate accuracy
accuracy = np.sum(np.array(predictions) == np.array(true_labels)) / len(true_labels) * 100

# Print the results
for image_path, label in results:
    print(f'Image: {image_path} - Prediction: {label}')

# Print the accuracy
print(f'Validation Accuracy: {accuracy:.2f}%')
