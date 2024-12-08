from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Flatten, Lambda
import tensorflow as tf
import matplotlib.pyplot as plt
from data_preparation import prepare_data
from signature_utils2 import load_pairs
from tensorflow.keras.callbacks import EarlyStopping

# Directories for training data
train_genuine_dir = 'C:/Users/krisa/Desktop/CPRO 2902/signature_verification_dataset2/train/genuine'
train_forged_dir = 'C:/Users/krisa/Desktop/CPRO 2902/signature_verification_dataset2/train/forged'

# Prepare training data
train_pairs, train_labels = prepare_data(train_genuine_dir, train_forged_dir)
X1_train, X2_train, y_train = load_pairs(train_pairs, train_labels)

# Base VGG16 model
def create_base_model():
    base_model = VGG16(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    x = Flatten()(base_model.output)
    x = Dense(512, activation="relu")(x)
    x = Dense(256, activation="relu")(x)
    return Model(base_model.input, x)


# Create the similarity model
def build_similarity_model():
    base_model = create_base_model()

    input_1 = Input(shape=(224, 224, 3))
    input_2 = Input(shape=(224, 224, 3))

    # Shared model for both inputs
    features_1 = base_model(input_1)
    features_2 = base_model(input_2)

    # Compute absolute difference
    diff = Lambda(lambda tensors: tf.abs(tensors[0] - tensors[1]))([features_1, features_2])

    # Fully connected layers
    x = Dense(128, activation="relu")(diff)
    x = Dense(64, activation="relu")(x)
    output = Dense(1, activation="sigmoid")(x)

    model = Model(inputs=[input_1, input_2], outputs=output)
    return model


# Build and compile the model
model = build_similarity_model()
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

# Initialize EarlyStopping callback
early_stopping = EarlyStopping(
    monitor='val_accuracy',  # Monitor validation accuracy
    patience=0,  # Stop immediately after no improvement
    restore_best_weights=True  # Restore model with best weights
)

try:
    # Train the model
    history = model.fit(
        [X1_train, X2_train],
        y_train,
        validation_split=0.2,
        batch_size=64,
        epochs=10,
        callbacks=[early_stopping]
    )
except KeyboardInterrupt:
    print("Training interrupted manually.")
finally:
    # Save the model after training is stopped
    model.save("signature_similarity_model.h5")
    print("Model saved as 'signature_similarity_model.h5'")

# Plot training and validation metrics
plt.figure(figsize=(12, 6))
plt.plot(history.history["accuracy"], label="Train Accuracy", marker="o")
plt.plot(history.history["val_accuracy"], label="Validation Accuracy", marker="o")
plt.title("Training and Validation Accuracy")
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(history.history["loss"], label="Train Loss", marker="o")
plt.plot(history.history["val_loss"], label="Validation Loss", marker="o")
plt.title("Training and Validation Loss")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)
plt.show()