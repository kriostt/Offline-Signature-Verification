from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import os

# Preprocess an image for VGG16 input
def preprocess_image(image_path):
    image = load_img(image_path, target_size=(224, 224))
    image = img_to_array(image)
    image = image / 255.0  # Normalize
    return image

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

# Compare an input signature against genuine signatures of a user
def compare_signatures(input_signature_path, user_genuine_dir, model, threshold=0.5):
    input_signature = preprocess_image(input_signature_path)
    input_signature = np.expand_dims(input_signature, axis=0)  # Add batch dimension

    # Filter and collect genuine signature files
    user_signatures = [
        os.path.join(user_genuine_dir, img)
        for img in os.listdir(user_genuine_dir)
        if img.endswith(('.png', '.jpg', '.jpeg'))
    ]

    similarities = []

    # Compare the input signature with each genuine signature
    for user_sig_path in user_signatures:
        user_signature = preprocess_image(user_sig_path)
        user_signature = np.expand_dims(user_signature, axis=0)  # Add batch dimension
        similarity = model.predict([input_signature, user_signature])[0][0]
        similarities.append(similarity)

    # Calculate average similarity
    avg_similarity = np.mean(similarities)

    # Determine result based on threshold
    result = "Genuine" if avg_similarity >= threshold else "Forged"

    return avg_similarity, result