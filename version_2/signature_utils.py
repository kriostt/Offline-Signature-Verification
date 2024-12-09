import numpy as np
import cv2
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Preprocess an image for VGG16 input
def preprocess_image(image_path):
    image = load_img(image_path, target_size=(224, 224))
    image = img_to_array(image)
    image = image / 255.0  # Normalize
    return image

def verify_signature(uploaded_signature, genuine_signatures, model, threshold=0.5):
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

# Load pairs of images and their labels
def load_pairs(pairs, labels):
    X1, X2, y = [], [], []
    for img1_path, img2_path in pairs:
        img1 = preprocess_image(img1_path)
        img2 = preprocess_image(img2_path)
        X1.append(img1)
        X2.append(img2)
        y.append(labels.pop(0))
    return np.array(X1), np.array(X2), np.array(y)
