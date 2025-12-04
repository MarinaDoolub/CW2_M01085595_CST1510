import bcrypt
import re
import time
import secrets
import sqlite3
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username
from app.data.schema import create_users_table

DATA_DIR = Path("DATA")
# Dictionary to track failed login attempts
failed_attempts = {} 
locked_accounts = {}
# Dictionary to track token sessions
sessions = {}
#-________________________________________________________________________-
#Checks the strength of a password

def check_password_strength(password):

    length = len(password)
    if length < 8:
        return "Weak"

    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

    common_patterns = ['123', 'password', 'qwerty', 'abc', 'letmein', 'admin']
    pattern_found = any(pattern.lower() in password.lower() for pattern in common_patterns)

    score = sum([has_lower, has_upper, has_digit, has_special])

    if pattern_found or score < 3:
        return "Weak"
    elif score == 3:
        return "Moderate"
    else:
        return "Strong"
    
#-________________________________________________________________________-

def create_session(username):
    # Generates a 16-byte token
    token = secrets.token_hex(16)   
    timestamp = time.time()        

    sessions[username] = (token, timestamp)
    return token

#-________________________________________________________________________-
#registers a new user
def register_user(conn, username, password, role):
    cursor = conn.cursor()
    create_users_table(conn)
    

   # Checks if user already exists
    exist = get_user_by_username(conn, username)
    if exist:
        return False, f"Username '{username}' already exists."

    # Checks the password strength
    strength = check_password_strength(password)
    if strength == "Weak":
        return False, "Password too weak! Must include uppercase, lowercase, digits & special characters."


    # Hash the password
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode('utf-8')

    # Insert new user
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()

    return True, f"User '{username}' registered successfully!"

#-________________________________________________________________________-
#logs in a user
def login_user(conn, username, password):
    cursor = conn.cursor()

    # Check if the account is currently locked
    now = time.time()
    if username in locked_accounts:
        if now < locked_accounts[username]:
            unlock_in = int(locked_accounts[username] - now)
            return False, f"Account locked. Try again in {unlock_in} seconds."
        else:
            # Unlock the account
            del locked_accounts[username]
            # resetting the failed attempts
            failed_attempts[username] = 0  

    # Find user
    user = get_user_by_username(conn, username)
    if not user:
        return False, "Username not found."

    # Verify password (user[2] is password_hash column)
    stored_hash = user[2]
    password_bytes = password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')

    if bcrypt.checkpw(password_bytes, hash_bytes):
        # Successful login which means reset the failed attempts
        failed_attempts[username] = 0

        # Creates the session token
        token = create_session(username)

        return True, f"Welcome, {username} Session token:{token}"
    
    else:
        # Increment the failed attempts
        failed_attempts[username] = failed_attempts.get(username, 0) + 1
        attempts_left = 3 - failed_attempts[username]

        if failed_attempts[username] >= 3:
            # Lock the account for 5 minutes
            locked_accounts[username] = now + 5 * 60  
            # reset attempts after locking
            failed_attempts[username] = 0  
            return False, "Account is now locked due to 3 failed attempts. Please try again in 5 minutes."
        else:
            return False, f"Invalid password. {attempts_left} attempt(s) left."
    
#-________________________________________________________________________-

def migrate_users_from_file(conn, filepath=DATA_DIR / "users.txt"):
    
    if not filepath.exists():
        print(f" File not found: {filepath}")
        print("  No users to migrate.")
        return

    cursor = conn.cursor()
    migrated_count = 0

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Parse line: username,password_hash
            parts = line.split(',')
            if len(parts) >= 2:
                username = parts[0]
                password_hash = parts[1]

                # Insert user (ignore if already exists)
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, 'user')
                    )
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except sqlite3.Error as e:
                    print(f"Error migrating user {username}: {e}")

    conn.commit()
    print(f" Migrated {migrated_count} users from {filepath.name}")

    # Query all users and verify if they migrated
    cursor.execute("SELECT user_id, username, role FROM users")
    users = cursor.fetchall()

    print(" Users in database:")
    print(f"{'ID':<5} {'Username':<15} {'Role':<10}")
    print("-" * 35)
    for user in users:
        print(f"{user[0]:<5} {user[1]:<15} {user[2]:<10}")

    print(f"\nTotal users: {len(users)}")