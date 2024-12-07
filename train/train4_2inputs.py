import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.utils import Sequence
import os

class SignaturePairGenerator(Sequence):
    def __init__(self, image_dir, batch_size, image_size=(224, 224), subset='training', shuffle=True):
        self.image_dir = image_dir
        self.batch_size = batch_size
        self.image_size = image_size
        self.subset = subset
        self.shuffle = shuffle
        self.genuine_images = self._load_image_paths('genuine')
        self.forged_images = self._load_image_paths('forged')
        self.on_epoch_end()

    def _load_image_paths(self, class_name):
        class_path = os.path.join(self.image_dir, class_name)
        image_paths = []
        for subfolder in os.listdir(class_path):
            subfolder_path = os.path.join(class_path, subfolder)
            if os.path.isdir(subfolder_path):
                image_paths.extend([os.path.join(subfolder_path, f) for f in os.listdir(subfolder_path) if f.endswith(('jpg', 'jpeg', 'png'))])
        return image_paths

    def __len__(self):
        return int(np.floor(min(len(self.genuine_images), len(self.forged_images)) / self.batch_size))

    def __getitem__(self, index):
        batch_genuine_paths = self.genuine_images[index * self.batch_size:(index + 1) * self.batch_size]
        batch_forged_paths = self.forged_images[index * self.batch_size:(index + 1) * self.batch_size]
        
        x1, x2, y = self.__data_generation(batch_genuine_paths, batch_forged_paths)
        return { "signature1": np.array(x1), "signature2": np.array(x2) }, np.array(y)  # Return as a dictionary

    def __data_generation(self, batch_genuine_paths, batch_forged_paths):
        x1 = []
        x2 = []
        y = []
        
        for path_genuine, path_forged in zip(batch_genuine_paths, batch_forged_paths):
            img1 = load_img(path_genuine, target_size=self.image_size)
            img2 = load_img(path_forged, target_size=self.image_size)
            
            img1 = img_to_array(img1) / 255.0
            img2 = img_to_array(img2) / 255.0
            
            x1.append(img1)
            x2.append(img2)
            
            # Label is 1 if the images are from the same person, 0 if from different persons
            label = 0  # Assume forged pairs for simplicity
            y.append(label)
        
        return np.array(x1), np.array(x2), np.array(y)

    def on_epoch_end(self):
        if self.shuffle:
            # Shuffle indices, not images themselves
            indices = np.arange(len(self.genuine_images))
            np.random.shuffle(indices)
            
            # Reorder the images according to shuffled indices
            self.genuine_images = np.array(self.genuine_images)[indices]
            self.forged_images = np.array(self.forged_images)[indices]


# Load Pre-trained VGG16 Model without the top classification layers
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Freeze the pre-trained layers

# Define the Input Layers for two signatures
input_signature1 = layers.Input(shape=(224, 224, 3), name="signature1")  # Input for uploaded signature
input_signature2 = layers.Input(shape=(224, 224, 3), name="signature2")  # Input for database signature

# Pass the inputs through the VGG16 base model
x1 = base_model(input_signature1)
x1 = layers.Flatten()(x1)
x2 = base_model(input_signature2)
x2 = layers.Flatten()(x2)

# Calculate the Euclidean distance between the feature vectors of the two signatures
distance = layers.Lambda(
    lambda tensors: tf.norm(tensors[0] - tensors[1], axis=1, keepdims=True),
    output_shape=(1,)
)([x1, x2])

# Add a Dense layer for classification (match or non-match)
x = layers.Dense(256, activation='relu')(distance)
x = layers.Dropout(0.5)(x)
output = layers.Dense(1, activation='sigmoid')(x)  # Binary classification: 1 for match, 0 for non-match

# Define the Model with two inputs and one output
model = Model(inputs={'signature1': input_signature1, 'signature2': input_signature2}, outputs=output)

# Compile the Model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Set up the training and validation generators
train_generator = SignaturePairGenerator(
    image_dir="C:/Users/krisa/Desktop/CPRO 2902/signature_verification_dataset3/train",  # Replace with your dataset path
    batch_size=32,
    image_size=(224, 224),
    subset='training'
)

validation_generator = SignaturePairGenerator(
    image_dir="C:/Users/krisa/Desktop/CPRO 2902/signature_verification_dataset3/validation",  # Replace with your dataset path
    batch_size=32,
    image_size=(224, 224),
    subset='validation'
)

# Train the Model
model.fit(train_generator, validation_data=validation_generator, epochs=15)

# Save the Model
model.save('verification_model.h5')
