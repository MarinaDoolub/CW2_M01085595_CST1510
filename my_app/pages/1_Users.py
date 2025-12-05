import streamlit as st
import pandas as pd
from openai import OpenAI
from app.data.db import connect_database
from my_app.sidebar import sidebar_navigation, ai_chat
from app.data.users import update_user_role,delete_user

#connection section
#___________________________-
if "conn" not in st.session_state:
    st.session_state.conn = connect_database()
conn = st.session_state.conn



# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""
    
# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")

    if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
    st.stop()

# If logged in, show dashboard content
st.title("📊 Multi-Intelligence Domain Platform")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

##initializing client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

#sidebar with its contents
category, filters = sidebar_navigation()
ai_chat(client)

st.subheader("Users")
try:
        users = pd.read_sql_query("SELECT * FROM users", st.session_state.conn)
        st.dataframe(users)
except Exception as e:
        st.error(f"Error fetching Users table:{e}")
    
st.markdown("---")
st.subheader("Insights on Users")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Users", len(users)) 

with col2:
    st.metric("Admins", (users["role"] == "admin").sum()) 

with col3:
    st.metric("Analysts", (users["role"] == "analyst").sum())  

with col4:
    st.metric("Viewers",(users["role"] == "viewer").sum())

st.subheader("Search/Filter Users")
search_username = st.text_input("Search by Username")
filter_role = st.selectbox("Filter by Role", ["All"] + users["role"].unique().tolist())

filtered_users = users.copy()
if search_username:
    filtered_users = filtered_users[filtered_users["username"].str.contains(search_username, case=False)]
    
    if filter_role != "All":
        filtered_users = filtered_users[filtered_users["role"] == filter_role]

    st.dataframe(filtered_users)

    st.markdown("---")
    st.subheader("Manage Users")

        #this will be for updating user role
    with st.expander("Update user role"):
        with st.form("Update_Role_Form"):
            username = st.text_input("Username")
            role = st.selectbox("New role",["Admin","Analyst","User","Viewer"])
            submit_update = st.form_submit_button("Update role")
                
            if submit_update:
                try:
                    rows = update_user_role(st.session_state.conn,username,role)
                    if rows > 0:
                        st.success(f"User {username} role updated to {role}")

                    else:
                        st.warning(f"No user found with ID {username}")

                except Exception as e:
                        st.error(f"Failed to update role: {e}")

        #this will be for deleting a user
    with st.expander("Delete user"):
        with st.form("Delete_User_Form"):
            user_id = st.number_input("Enter the user ID to be deleted", min_value=1, step=1)
            submit_delete = st.form_submit_button("Delete user")
                
            if submit_delete:
                try:
                    rows = delete_user(st.session_state.conn,user_id)
                    if rows > 0:
                        st.success(f"User {user_id} deleted successfully")

                    else:
                        st.warning(f"No users found with ID {user_id}")

                except Exception as e:
                    st.error(f"Failed to delete  user: {e}")

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")

if not st.session_state.logged_in:
    st.error("You must be logged in...")
    st.switch_page("Home.py")
st.stop()