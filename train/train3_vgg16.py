import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models # type: ignore
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore

# Load Pre-trained VGG16 Model
base_model = tf.keras.applications.VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Freeze the base model

# Add Custom Layers for Signature Verification
model = models.Sequential([
    base_model,
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(1, activation='sigmoid')  # Binary classification
])

# Compile the Model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Data Preparation
datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)
train_generator = datagen.flow_from_directory(
    "C:/Users/krisa/Desktop/CPRO 2902/signature_verification_dataset4/train",  # Replace with your dataset path
    target_size=(224, 224),
    class_mode='binary',
    subset='training'
)
validation_generator = datagen.flow_from_directory(
    "C:/Users/krisa/Desktop/CPRO 2902/signature_verification_dataset4/validation",  # Replace with your dataset path
    target_size=(224, 224),
    class_mode='binary',
    subset='validation'
)

# Train the Model
model.fit(train_generator, validation_data=validation_generator, epochs=5)

# Save the Model
model.save('verification_model7.h5')
