import streamlit as st
import pickle
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# -------------------------------
# Load model & vectorizer
# -------------------------------
def load_model():
    try:
        with open("model.pkl", "rb") as model_file:
            model = pickle.load(model_file)
        with open("vectorizer.pkl", "rb") as vec_file:
            vectorizer = pickle.load(vec_file)
        return model, vectorizer
    except FileNotFoundError:
        return None, None

model, vectorizer = load_model()

# -------------------------------
# Database helper functions
# -------------------------------
def get_connection():
    return sqlite3.connect("health.db", check_same_thread=False)

def get_advice(disease):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT advice FROM health_data WHERE disease=?", (disease,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "No advice available."

def fetch_all_records():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM health_data", conn)
    conn.close()
    return df

def fetch_one_record(record_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT symptoms, disease, advice FROM health_data WHERE id=?", (record_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def insert_record(symptoms, disease, advice):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO health_data (symptoms, disease, advice) VALUES (?, ?, ?)",
                   (symptoms, disease, advice))
    conn.commit()
    conn.close()

def update_record(record_id, symptoms, disease, advice):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE health_data SET symptoms=?, disease=?, advice=? WHERE id=?",
                   (symptoms, disease, advice, record_id))
    conn.commit()
    conn.close()

def delete_record(record_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM health_data WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

def validate_admin(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin_users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# -------------------------------
# Retrain ML Model
# -------------------------------
def retrain_model():
    global model, vectorizer
    df = fetch_all_records()

    if df.empty or len(df) < 2:
        return False, "⚠️ Not enough data in database to train the model."

    X = df["symptoms"]
    y = df["disease"]

    vectorizer = CountVectorizer()
    X_vec = vectorizer.fit_transform(X)

    model = MultinomialNB()
    model.fit(X_vec, y)

    with open("model.pkl", "wb") as model_file:
        pickle.dump(model, model_file)
    with open("vectorizer.pkl", "wb") as vec_file:
        pickle.dump(vectorizer, vec_file)

    return True, "✅ Model retrained successfully!"

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Health Diagnostics Chatbot", page_icon="🩺")

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🤖 User Chatbot", "🛠️ Admin Panel"])

if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# -------------------------------
# User Page
# -------------------------------
if page == "🤖 User Chatbot":
    st.title("🩺 Health Diagnostics Chatbot")
    st.write("Enter your symptoms and get instant health advice.")

    user_input = st.text_input("Your symptoms (comma or space separated):", placeholder="e.g., fever, headache, sore throat")

    if st.button("Diagnose"):
        if not user_input.strip():
            st.warning("⚠️ Please enter symptoms.")
        elif model is None or vectorizer is None:
            st.error("❌ Model not trained yet. Please ask an Admin to set up and train the model.")
        else:
            try:
                X_test = vectorizer.transform([user_input])
                prediction = model.predict(X_test)[0]
                health_advice = get_advice(prediction)

                st.success(f"🔎 **Predicted Condition:** {prediction}")
                st.info(f"💡 **Suggested Advice:** {health_advice}")
            except Exception as e:
                st.error(f"An error occurred during diagnosis: {e}")

# -------------------------------
# Admin Page
# -------------------------------
elif page == "🛠️ Admin Panel":
    st.title("🛠️ Admin Panel")

    if not st.session_state.logged_in:
        st.subheader("🔐 Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if validate_admin(username, password):
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("❌ Invalid username or password.")
    else:
        st.success("✅ Logged in as Admin")
        st.sidebar.markdown("---")
        option = st.sidebar.radio("Admin Actions", ["View Records", "Add Record", "Update Record", "Delete Record", "Retrain Model"])

        if option == "View Records":
            st.subheader("📋 All Health Records")
            df = fetch_all_records()
            st.dataframe(df, use_container_width=True)

        elif option == "Add Record":
            st.subheader("➕ Add New Record")
            with st.form("add_form", clear_on_submit=True):
                symptoms = st.text_input("Symptoms")
                disease = st.text_input("Disease")
                advice = st.text_area("Advice")
                submitted = st.form_submit_button("Add Record")
                if submitted:
                    if symptoms and disease and advice:
                        insert_record(symptoms, disease, advice)
                        st.success("✅ Record added successfully!")
                    else:
                        st.warning("⚠️ Please fill all fields.")

        elif option == "Update Record":
            st.subheader("✏️ Update Record")
            df = fetch_all_records()
            st.dataframe(df, use_container_width=True)
            
            record_id = st.number_input("Enter Record ID to Update", min_value=1, step=1)
            
            if record_id:
                record_data = fetch_one_record(record_id)
                if record_data:
                    with st.form("update_form"):
                        st.write(f"**Editing Record ID: {record_id}**")
                        symptoms, disease, advice = record_data
                        
                        new_symptoms = st.text_input("Symptoms", value=symptoms)
                        new_disease = st.text_input("Disease", value=disease)
                        new_advice = st.text_area("Advice", value=advice)
                        
                        updated = st.form_submit_button("Update Record")
                        if updated:
                            update_record(record_id, new_symptoms, new_disease, new_advice)
                            st.success(f"✅ Record ID {record_id} updated successfully!")
                            st.experimental_rerun()
                else:
                    st.warning("Record ID not found.")

        elif option == "Delete Record":
            st.subheader("🗑️ Delete Record")
            df = fetch_all_records()
            st.dataframe(df, use_container_width=True)
            
            record_id = st.number_input("Enter Record ID to Delete", min_value=1, step=1)
            if record_id:
                st.warning(f"**Warning:** You are about to delete record ID {record_id}. This action cannot be undone.")
                if st.button("Confirm Deletion"):
                    delete_record(record_id)
                    st.success(f"✅ Record ID {record_id} deleted successfully!")
                    st.experimental_rerun()

        elif option == "Retrain Model":
            st.subheader("🔄 Retrain ML Model")
            st.write("Click the button below to retrain the model with the current data in the database.")
            st.warning("This may take a few moments.")
            if st.button("Retrain Now"):
                with st.spinner("Training in progress..."):
                    success, msg = retrain_model()
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)









