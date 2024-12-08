from tensorflow.keras.models import load_model
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, classification_report
from new_model.data_preparation import create_pairs_for_test
from signature_utils import load_pairs

# Directories for test data
test_genuine_dir = 'path_to_test_set/genuine'
test_forged_dir = 'path_to_test_set/forged'

# Prepare test data
db_signatures, test_inputs, test_labels = create_pairs_for_test(test_genuine_dir, test_forged_dir, test_users=None)
X1_test, X2_test, y_test = load_pairs(
    [(db, inp) for db in db_signatures for inp in test_inputs],
    [lbl for lbl in test_labels for _ in range(len(db_signatures))]
)

# Load the trained model
model = load_model("signature_similarity_model.h5")
print("Model loaded successfully.")

# Evaluate the model on the test set
print("\nEvaluating on test set:")
y_pred_probs = model.predict([X1_test, X2_test])
y_pred = (y_pred_probs > 0.5).astype(int)

# Metrics
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Forged", "Genuine"]))

print("\nConfusion Matrix:")
print(conf_matrix)