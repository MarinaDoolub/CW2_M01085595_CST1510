from app.data.db import connect_database, DB_PATH
from app.data.schema import create_all_tables
from app.services.user_service import migrate_users_from_file
from app.data.datasets import load_all_csv_data

conn = connect_database()
load_all_csv_data(conn)
conn.close()


def setup_database_complete():

    print("\n" + "="*60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("="*60)

    # Step 1: Connect
    print("\n[1/5] Connecting to database...")
    conn = connect_database()
    print("       Connected")

    # Step 2: Create tables
    print("\n[2/5] Creating database tables...")
    create_all_tables(conn)

    # Step 3: Migrate users
    print("\n[3/5] Migrating users from users.txt...")
    user_count = migrate_users_from_file(conn)
    print(f"       Migrated {user_count} users")

    # Step 4: Load CSV data
    print("\n[4/5] Loading CSV data...")
    total_rows = load_all_csv_data(conn)

    # Step 5: Verify
    print("\n[5/5] Verifying database setup...")
    cursor = conn.cursor()

    # Count rows in each table
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n Database Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<15}")

    conn.close()

    print("\n" + "="*60)
    print(" DATABASE SETUP COMPLETE!")
    print("="*60)
    print(f"\n Database location: {DB_PATH.resolve()}")
    print("\nYou're ready for Week 9 (Streamlit web interface)!")

# Run the complete setup
if __name__ == "__main__":
    setup_database_complete()