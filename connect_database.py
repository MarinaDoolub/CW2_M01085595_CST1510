import sqlite3
from pathlib import Path

# Set the database path (file will be created automatically if missing)
DB_PATH = Path("database.db")

def connect_database(db_path=DB_PATH):
    """
    Connect to the SQLite database.
    Creates the database file if it doesn't exist.

    Args:
        db_path: Path to the database file

    Returns:
        sqlite3.Connection: Database connection object
    """
    return sqlite3.connect(str(db_path))


# Test connection
if __name__ == "__main__":
    conn = connect_database()
    print("Connected successfully!")
    conn.close()