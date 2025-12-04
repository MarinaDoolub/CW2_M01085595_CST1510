import pandas as pd
from pathlib import Path

#insert csv data into table that was created
def load_csv_to_table(conn, csv_path, table_name):
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f" CSV file not found: {csv_file}")
        return 0

    try:
        # Read the CSV
        df = pd.read_csv(csv_file)

        # Ensuring the columns exist before insertion
        ensure_columns_exist(conn, table_name, df)

        # Insert the rows
        df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
        row_count = len(df)
        
        print(f"Successfully loaded {row_count} rows from {csv_file.name} into table '{table_name}'")
        return row_count
    
    except Exception as e:
        print(f"Error loading CSV into table: {e}")
        return 0
#-----------------------------------------------------
#load the data from csv 
def load_all_csv_data(conn):
    # __file__ is the current script path
    current_dir = Path(__file__).parent  
    project_root = current_dir.parent.parent  

    data_dir = project_root / "DATA"

    csv_files = {
        "cyber_incidents": data_dir / "cyber_incidents.csv",
        "it_tickets": data_dir / "it_tickets.csv",
        "datasets_metadata": data_dir / "datasets_metadata.csv"
    }

    total = 0
    for table, path in csv_files.items():
        if not path.exists():
            print(f"CSV file not found: {path}")
            continue
        print(f"Loading {path} into {table}...")
        total += load_csv_to_table(conn, path, table)

    print(f"\nTotal rows loaded: {total}")
    return total


#-----------------------------------------------------
def ensure_columns_exist(conn, table_name, df):
    cursor = conn.cursor()

    # Get existing columns in the table
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_cols = [col[1] for col in cursor.fetchall()]

    # Add any missing columns
    for col in df.columns:
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} TEXT")
            print(f"Added missing column: {col}")

    conn.commit()