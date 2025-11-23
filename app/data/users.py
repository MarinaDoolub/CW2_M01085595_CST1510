from app.data.db import connect_database
import bcrypt

#------------------------------------------------------------------------
def get_user_by_username(conn, username):
    #Retrieve user by username
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
def insert_user(conn, username, plain_password, role='user'):

    # Hash the password
    password_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode('utf-8')

    # Connect to database and insert user
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()

    #this is to return the inserted user ID
    last_id = cursor.lastrowid
    conn.close()

    return last_id

#------------------------------------------------------------------------
def update_user_role(conn, username, new_role):
   #update user role
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
#------------------------------------------------------------------------

def delete_user(conn, user_id):
    #delete user ID
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        rowcount = cursor.rowcount
    
    except Exception as e:
        print(f"Error deleting user ID {user_id}: {e}")
        rowcount = 0

    conn.close()
    return rowcount

