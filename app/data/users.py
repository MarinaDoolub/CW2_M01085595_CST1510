from app.data.db import connect_database
import bcrypt

#------------------------------------------------------------------------
def get_user_by_username(username):
    #Retrieve user by username
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return user

#------------------------------------------------------------------------
#create new user and hash password
def insert_user(username, plain_password, role='user'):

    # Hash the password
    password_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    # Connect to database and insert user
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hashed, role)
    )
    conn.commit()

    #this is to return the inserted user ID
    last_id = cursor.lastrowid
    conn.close()

    return last_id

#------------------------------------------------------------------------
def update_user_role(username, new_role):
   #update user role
    conn = connect_database()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE users SET role = ? WHERE username = ?",
            (new_role, username)
        )
        conn.commit()
        rowcount = cursor.rowcount

    except Exception as e:
        print(f"Error updating role for '{username}': {e}")
        rowcount = 0
    finally:
        conn.close()
        return rowcount