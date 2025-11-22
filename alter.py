from app.data.db import connect_database

#Altered id to user_id
conn = connect_database()
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users RENAME COLUMN id TO user_id;")
    conn.commit()
    print("Column renamed to user_id successfully!")
except Exception as e:
    print("Rename skipped or failed:", e)

#________________________________
def alter_tables_for_csv():
    conn = connect_database()
    cursor = conn.cursor()

    try:
        #Cyber incidents table 
        # Add incident_id if missing
        cursor.execute("PRAGMA table_info(cyber_incidents)")
        columns = [col[1] for col in cursor.fetchall()]
        if "incident_id" not in columns:
            cursor.execute("ALTER TABLE cyber_incidents ADD COLUMN incident_id INTEGER;")
            print("Added 'incident_id' column to cyber_incidents")

        # IT tickets table
        cursor.execute("PRAGMA table_info(it_tickets)")
        columns = [col[1] for col in cursor.fetchall()]
        if "resolution_time_hours" not in columns:
            cursor.execute("ALTER TABLE it_tickets ADD COLUMN resolution_time_hours REAL;")
            print("Added 'resolution_time_hours' column to it_tickets")

        # Datasets metadata table
        cursor.execute("PRAGMA table_info(datasets_metadata)")
        columns = [col[1] for col in cursor.fetchall()]
        if "dataset_id" not in columns:
            cursor.execute("ALTER TABLE datasets_metadata ADD COLUMN dataset_id INTEGER;")
            print("Added 'dataset_id' column to datasets_metadata")

        conn.commit()
        print("\nAll missing columns added successfully!")

    except Exception as e:
        print("Error altering tables:", e)

    finally:
        conn.close()


if __name__ == "__main__":
    alter_tables_for_csv()