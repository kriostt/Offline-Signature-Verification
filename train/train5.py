import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.utils import Sequence
import os


class SignaturePairGenerator(Sequence):
    def __init__(self, image_dir, batch_size, image_size=(224, 224), shuffle=True):
        self.image_dir = image_dir
        self.batch_size = batch_size
        self.image_size = image_size
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
        return {"signature1": np.array(x1), "signature2": np.array(x2)}, np.array(y)
    
    def __data_generation(self, batch_genuine_paths, batch_forged_paths):

        x1 = []
        x2 = []
        y = []
        
        for genuine_path, forged_path in zip(batch_genuine_paths, batch_forged_paths):
            # Load images
            genuine_img = load_img(genuine_path, target_size=self.image_size)
            forged_img = load_img(forged_path, target_size=self.image_size)
            
            genuine_img = img_to_array(genuine_img) / 255.0
            forged_img = img_to_array(forged_img) / 255.0

            # Matching pair (label 1)
            x1.append(genuine_img)
            x2.append(genuine_img)  # Pair with itself
            y.append(1)
            
            # Non-matching pair (label 0)
            x1.append(genuine_img)
            x2.append(forged_img)  # Pair with forged signature
            y.append(0)

        return np.array(x1), np.array(x2), np.array(y)

    def on_epoch_end(self):
        if self.shuffle:
            # Create a single set of indices for shuffling both genuine and forged images together
            indices = np.arange(len(self.genuine_images))
            np.random.shuffle(indices)
            
            # Apply the same shuffled indices to both genuine and forged images
            self.genuine_images = [self.genuine_images[i] for i in indices]
            self.forged_images = [self.forged_images[i] for i in indices]


# Define model
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

input_signature1 = layers.Input(shape=(224, 224, 3), name="signature1")
input_signature2 = layers.Input(shape=(224, 224, 3), name="signature2")

x1 = base_model(input_signature1)
x1 = layers.Flatten()(x1)
x2 = base_model(input_signature2)
x2 = layers.Flatten()(x2)

distance = layers.Lambda(
    lambda tensors: tf.norm(tensors[0] - tensors[1], axis=1, keepdims=True),
    output_shape=(1,)
)([x1, x2])


x = layers.Dense(256, activation='relu')(distance)
x = layers.Dropout(0.5)(x)
output = layers.Dense(1, activation='sigmoid')(x)

model = Model(inputs={'signature1': input_signature1, 'signature2': input_signature2}, outputs=output)

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])

# Generators
train_generator = SignaturePairGenerator(
    image_dir="/Users/alessandrahenriz/Desktop/Offline-Signature-Verification/CEDAR_signatures/train",
    batch_size=32,
    image_size=(224, 224),
)

validation_generator = SignaturePairGenerator(
    image_dir="/Users/alessandrahenriz/Desktop/Offline-Signature-Verification/CEDAR_signatures/validation",
    batch_size=32,
    image_size=(224, 224),
)

# Train the model
model.fit(train_generator, validation_data=validation_generator, epochs=15)

# Save the model
model.save('verification_model_improved.h5')
