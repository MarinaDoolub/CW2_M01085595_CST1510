import sqlite3
from pathlib import Path

#define paths
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    #create DATA directory if it doesn't exist

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    #connect to database
    conn = sqlite3.connect(str(db_path))

    print("Imports successful!")
    print("Database connected successfully!")
    print(f"DATA folder:{DATA_DIR.resolve()}")
    print(f"Database located at:{db_path.resolve()}")

    return conn

if __name__ == "__main__":
    connect_database()