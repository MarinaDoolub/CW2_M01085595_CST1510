import streamlit as st
import os
import sys



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
st.set_page_config(page_title="Multi-Intelligence Domain Platform", page_icon="📊",layout="wide")


from app.data.db import connect_database
from app.services.user_service import register_user, login_user
from app.data.load import load_all_csv_data
from app.data.users import get_user_by_username
from app.data.schema import create_all_tables

st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")

#database connection
if "conn" not in st.session_state:
    st.session_state.conn = connect_database()
    create_all_tables(st.session_state.conn)
    load_all_csv_data(st.session_state.conn)


# ---------- Initialise session state ----------
if "users" not in st.session_state:
    # Very simple in-memory "database": {username: password}
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""
   
st.title("🔐 Welcome")

# If already logged in, go straight to dashboard (optional)
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
        
    if st.button("Go to User's dashboard"):
    # Use the official navigation API to switch pages
        st.switch_page("pages/1_Users.py") # path is relative to Home.py :contentReference[oaicite:1]{index=1}
        st.stop() # Don’t show login/register again

# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username",key="login_username")
    login_password = st.text_input("Password", type="password",key="login_password")

    if st.button("Log in"):
    # Simple credential check (for teaching only – not secure!)
        success, message = login_user(st.session_state.conn, login_username, login_password)
                
        if success:
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.success(f"Welcome back, {login_username}! 🎉 ")
            # Redirect to dashboard page
            st.switch_page("pages/1_Users.py")
        else:
            st.error(message)

        
# ----- REGISTER TAB -----
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username",key="register_username")
    new_password = st.text_input("Choose a password",type="password", key="register_password")
    confirm_password = st.text_input("Confirm password",type="password", key="register_confirm")

    role = st.selectbox("Select your role", ["Admin", "Analyst", "User", "Viewer"])

    if st.button("Create account"):
    # Basic checks – again, just for teaching
        if not new_username or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        
        else:
            existing_user = get_user_by_username(st.session_state.conn, new_username)
            if existing_user:
                st.error("Username already exists. Choose another one.")

            else:
                success, message = register_user(st.session_state.conn, new_username, new_password, role)

                if success:
                    st.success("Account created! You can now log in from the Login tab.")
                    st.info("Tip: go to the Login tab and sign in with your new account.")
                else:
                    st.error(message)