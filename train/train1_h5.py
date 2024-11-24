import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense # type: ignore
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.utils import to_categorical # type: ignore
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore

def load_and_preprocess_image(path, label):
    image = cv2.imread(path)
    if image is not None:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, (224, 224))
        return image, label
    else:
        return None, None

# Path to the genuine signatures
genuine_path = "C:/Users/krisa/Desktop/CPRO 2902/signature_verification_dataset/sign_data/test/genuine"

# Path to the forged signatures
forged_path = "C:/Users/krisa/Desktop/CPRO 2902/signature_verification_dataset/sign_data/test/forged"

# Walk through the genuine signature folder
genuine_images_and_labels = []
for root, _, files in os.walk(genuine_path):
    for f in files:
        img, lbl = load_and_preprocess_image(os.path.join(root, f), 0)
        if img is not None:
            genuine_images_and_labels.append((img, lbl))

# Walk through the forged signature folder
forged_images_and_labels = []
for root, _, files in os.walk(forged_path):
    for f in files:
        img, lbl = load_and_preprocess_image(os.path.join(root, f), 1)
        if img is not None:
            forged_images_and_labels.append((img, lbl))

# Extract images and labels
genuine_images = np.array([img for img, lbl in genuine_images_and_labels]) / 255.0
forged_images = np.array([img for img, lbl in forged_images_and_labels]) / 255.0

genuine_labels = np.zeros(len(genuine_images))
forged_labels = np.ones(len(forged_images))

images = np.concatenate((genuine_images, forged_images))
labels = np.concatenate((genuine_labels, forged_labels))

# Convert labels to categorical (for binary classification)
labels = to_categorical(labels, num_classes=2)

# Split dataset
X_train, X_val, y_train, y_val = train_test_split(images, labels, test_size=0.2, random_state=42)

# Reshape images for the model (adding the channel dimension)
X_train = X_train.reshape(-1, 224, 224, 1)
X_val = X_val.reshape(-1, 224, 224, 1)

# Build the model
model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(224, 224, 1)))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(2, activation='softmax'))  # Binary classification

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Initialize the ImageDataGenerator
datagen = ImageDataGenerator(
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    horizontal_flip=False,
    fill_mode='nearest'
)

# Fit the generator on the training data
datagen.fit(X_train)

# Train the model using augmented data
model.fit(datagen.flow(X_train, y_train, batch_size=32), 
          epochs=50, 
          validation_data=(X_val, y_val))

# Save the model after training
model.save("C:/Users/krisa/Desktop/CPRO 2902/Offline-Signature-Verification/signature_verification_model.h5")

# Evaluate the model
validation_score = model.evaluate(X_val, y_val, verbose=0)[1]
print('Validation Score:', validation_score)
