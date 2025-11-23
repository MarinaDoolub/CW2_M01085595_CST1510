from app.data.db import connect_database
import bcrypt

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
