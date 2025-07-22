import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle


df=pd.read_csv(r'C:\Users\kavyasree\Desktop\skill_gap_analyzer\data\job_training_data.csv')

vectorizer=TfidfVectorizer()
X=vectorizer.fit_transform(df['skills'])
y=df['job_title']

model=LogisticRegression()
model.fit(X,y)

with open('models/job_classifier.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('models/tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("✅ Job classifier trained and saved!")