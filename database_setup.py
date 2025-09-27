import sqlite3

# Connect / create database
conn = sqlite3.connect("health.db")
cursor = conn.cursor()

# -------------------------------
# Create tables
# -------------------------------
# Table for health data
cursor.execute("""
CREATE TABLE IF NOT EXISTS health_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symptoms TEXT NOT NULL,
    disease TEXT NOT NULL,
    advice TEXT NOT NULL
)
""")

# Table for admin users
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# -------------------------------
# Insert sample health data
# -------------------------------
# Clear existing data to avoid duplicates on re-run
cursor.execute("DELETE FROM health_data")

sample_data = [
    ("fever, cough, tiredness", "Flu", "Take rest, drink fluids, and consult a doctor if severe."),
    ("chest pain, shortness of breath", "Heart Disease", "Seek immediate medical help immediately."),
    ("frequent urination, increased thirst", "Diabetes", "Monitor blood sugar and consult a doctor."),
    ("sneezing, itchy eyes, runny nose", "Allergy", "Avoid allergens and take antihistamines."),
    ("headache, nausea, light sensitivity", "Migraine", "Rest in a dark room, take prescribed medicine."),
    ("fever, body pain, weakness", "Dengue", "Stay hydrated, rest, and consult a doctor for blood tests."),
    ("sore throat, cough, runny nose", "Cold", "Rest, drink warm fluids, and take cough medicine if necessary."),
    ("vomiting, stomach pain, diarrhea", "Food Poisoning", "Drink plenty of water, eat light food, consult a doctor if severe."),
    ("joint pain, fatigue, rash", "Chikungunya", "Rest, drink fluids, and take prescribed pain relievers."),
    ("fever, rash, red eyes", "Measles", "Isolate, drink fluids, and consult a doctor."),
    ("yellow skin, fatigue, dark urine", "Jaundice", "Consult a doctor for liver function tests and follow their advice on diet and rest."),
    ("persistent cough, chest pain, weight loss", "Tuberculosis", "Seek medical attention immediately for proper diagnosis and treatment with antibiotics."),
    ("high fever, headache, stomach pain", "Typhoid", "Consult a doctor for diagnosis. Requires antibiotic treatment and proper hydration.")
]

cursor.executemany("INSERT INTO health_data (symptoms, disease, advice) VALUES (?, ?, ?)", sample_data)

# -------------------------------
# Insert default admin
# -------------------------------
# Using INSERT OR IGNORE to prevent an error if the admin already exists
cursor.execute("INSERT OR IGNORE INTO admin_users (username, password) VALUES (?, ?)", ("admin", "admin123"))

# -------------------------------
# Commit and close
# -------------------------------
conn.commit()
conn.close()

print("✅ Database setup complete! Admin -> (username=admin, password=admin123)")
