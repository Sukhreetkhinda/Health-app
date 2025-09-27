import sqlite3
import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# -------------------------------
# Connect to database
# -------------------------------
conn = sqlite3.connect("health.db")
df = pd.read_sql_query("SELECT symptoms, disease FROM health_data", conn)
conn.close()

# -------------------------------
# Check if database has data
# -------------------------------
if df.empty:
    print("⚠️ No data found in database. Please run database_setup.py first.")
else:
    X = df["symptoms"]
    y = df["disease"]

    # -------------------------------
    # Vectorize symptoms
    # -------------------------------
    vectorizer = CountVectorizer()
    X_vec = vectorizer.fit_transform(X)

    # -------------------------------
    # Train Naive Bayes Model
    # -------------------------------
    model = MultinomialNB()
    model.fit(X_vec, y)

    # -------------------------------
    # Save Model & Vectorizer
    # -------------------------------
    with open("model.pkl", "wb") as model_file:
        pickle.dump(model, model_file)
    with open("vectorizer.pkl", "wb") as vec_file:
        pickle.dump(vectorizer, vec_file)

    print("✅ Model trained and saved as model.pkl & vectorizer.pkl")