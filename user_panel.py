import streamlit as st
import sqlite3
import hashlib

# -------------------------------
# Database Connection
# -------------------------------
def get_connection():
    return sqlite3.connect("health.db", check_same_thread=False)

# -------------------------------
# Password Hashing
# -------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------------
# User Functions
# -------------------------------
def register_user(username, email, password, full_name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)",
            (username, email, hash_password(password), full_name),
        )
        conn.commit()
        return True, "✅ Registration successful! You can now log in."
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "⚠️ Username already exists."
        elif "email" in str(e):
            return False, "⚠️ Email already registered."
        else:
            return False, "⚠️ Registration failed."
    finally:
        conn.close()

def validate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password)),
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

# -------------------------------
# Streamlit UI
# -------------------------------
def user_panel():
    st.sidebar.title("User Panel")
    page = st.sidebar.radio("Go to", ["Login", "Register"])

    if page == "Register":
        st.subheader("📝 Create an Account")
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")

            if submitted:
                if not (username and email and password and confirm_password):
                    st.warning("⚠️ Please fill in all fields.")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match.")
                else:
                    success, msg = register_user(username, email, password, full_name)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    elif page == "Login":
        st.subheader("🔑 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if validate_user(username, password):
                st.session_state["user_logged_in"] = True
                st.session_state["username"] = username
                st.success(f"✅ Welcome, {username}!")
            else:
                st.error("❌ Invalid username or password.")

    # Logout option
    if st.session_state.get("user_logged_in", False):
        if st.sidebar.button("Logout"):
            st.session_state["user_logged_in"] = False
            st.session_state["username"] = ""
            st.experimental_rerun()
