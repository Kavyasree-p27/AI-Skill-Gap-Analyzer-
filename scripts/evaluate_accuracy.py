import pandas as pd
import pickle
from sklearn.metrics import classification_report, accuracy_score

# Load test/training data
df = pd.read_csv('data/job_training_data.csv')

# Split features and labels
X_text = df['skills']
y_true = df['job_title']

# Load trained model and vectorizer
with open('models/job_classifier.pkl', 'rb') as f:
    model = pickle.load(f)

with open('models/tfidf_vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Transform skills text into vectors
X = vectorizer.transform(X_text)

# Predict job roles
y_pred = model.predict(X)

# Evaluate performance
print("\n🔍 Classification Report:\n")
print(classification_report(y_true, y_pred))

print("Accuracy Score:", round(accuracy_score(y_true, y_pred) * 100, 2), "%")
