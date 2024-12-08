import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load the trained model
model = load_model("C:/Users/krisa/Desktop/CPRO 2902/Offline-Signature-Verification/verification_model.h5")

def preprocess_image(image):
    # Preprocess image for the model
    if isinstance(image, str):  # File path
        img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    else:  # Numpy array
        img = image

    img = cv2.resize(img, (224, 224))  # Resize to 224x224
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)  # Convert to 3 channels
    img = img / 255.0  # Normalize
    return np.expand_dims(img, axis=0)

def verify_signature(uploaded_signature, genuine_signatures, threshold=0.5):
    # Verify a signature against stored signatures
    similarity_scores = []
    for genuine_image_data in genuine_signatures:
        genuine_image = np.frombuffer(genuine_image_data, dtype=np.uint8)
        genuine_image = cv2.imdecode(genuine_image, cv2.IMREAD_GRAYSCALE)
        genuine_image = preprocess_image(genuine_image)

        similarity = model.predict([uploaded_signature, genuine_image])[0][0]
        similarity_scores.append(similarity)

    max_score = max(similarity_scores)
    return max_score, max_score > threshold
