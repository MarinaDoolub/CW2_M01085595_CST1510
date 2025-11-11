import bcrypt
import os

USER_DATA_FILE = "users.txt"


def hash_password(plain_text_password):
    password_bytes = plain_text_password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt)


def verify_password(plain_text_password, hashed_password):
    password_bytes = plain_text_password.encode("utf-8")
    if isinstance(hashed_password):
        hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password)


def load_users():
    users = {}
    if not os.path.exists(USER_DATA_FILE):
        return users

    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue
            parts = raw.split(",", 1)
            if len(parts) != 2:
                continue
            username = parts[0].strip()
            stored_hash = parts[1].strip()
            if username:
                users[username] = stored_hash
    return users


def register_user(username, password):
    username = username.strip()
    if not username:
        print("Error: Username cannot be empty.")
        return False

    # Load current users and check duplicates
    users = load_users()
    if username in users:
        print(f"\n Error: The username '{username}' already exists. Please choose another.")
        return False

    # Hash and append to file
    hashed = hash_password(password)
    try:
        with open(USER_DATA_FILE, "a", encoding="utf-8") as f:
            f.write(f"{username},{hashed.decode('utf-8')}\n")
        print(f"\n User '{username}' registered successfully.")
        return True
    except Exception as e:
        print(f"Error writing to file: {e}")
        return False


def login_user(username, password):
    users = load_users()
    if username not in users:
        return "Username not found"
    stored_hash = users[username]
    if verify_password(password, stored_hash):
        return "Success"
    else:
        return "Wrong password"


def validate_username(username):
    if len(username.strip()) < 3:
        return False, "Username must be at least 3 characters long."
    if "," in username:
        return False, "Username cannot contain commas."
    return True, None


def validate_password(password):

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, None


def display_menu():

    print("\n" + "=" * 50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("=" * 50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] View registered users")
    print("[4] Exit")
    print("-" * 50)


def main():
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-4): ").strip()

        if choice == '1':
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()
            is_valid, err = validate_username(username)
            if not is_valid:
                print(f"Error: {err}")
                continue

            password = input("Enter a password: ").strip()
            is_valid, err = validate_password(password)
            if not is_valid:
                print(f"Error: {err}")
                continue

            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            register_user(username, password)

        elif choice == '2':
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            result = login_user(username, password)

            if result == "success":
                print("\n You are now logged in.")
                input("\nPress Enter to return to the main menu...")
            elif result == "Username not found":
                print("\nError: Username not found.")  
            elif result == "Wrong password":
                print("\nError: Incorrect password.")

        elif choice == '3':
            print("\n--- REGISTERED USERS ---")
            users = load_users()
            if not users:
                print("No users registered yet.")
            else:
                print("Currently registered usernames:")
                for user in sorted(users.keys()):
                    print(f" - {user}")
            input("\nPress Enter to return to the main menu...")

        elif choice == '4':
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1 - 4.")


if __name__ == "__main__":
    main()
