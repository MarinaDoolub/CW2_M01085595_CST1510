import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
#define paths
DATA_DIR = PROJECT_ROOT / "DATA"
DB_PATH = DATA_DIR / "intelligence_platform.db"

def connect_database(db_path: Path=DB_PATH):
    #create DATA directory if it doesn't exist

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    #connect to database
    conn = sqlite3.connect(str(db_path), check_same_thread=False)

    print("Imports successful!")
    print("Database connected successfully!")
    print(f"DATA folder:{DATA_DIR.resolve()}")
    print(f"Database located at:{db_path.resolve()}")

    return conn

if __name__ == "__main__":
    connect_database()