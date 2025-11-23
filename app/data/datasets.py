import pandas as pd
from pathlib import Path

#insert csv data into table that was created
def load_csv_to_table(conn, csv_path, table_name):
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f" CSV file not found: {csv_file}")
        return 0

    try:
        df = pd.read_csv(csv_file)
        df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
        row_count = len(df)
        print(f"Successfully loaded {row_count} rows from {csv_file.name} into table '{table_name}'")
        return row_count
    
    except Exception as e:
        print(f"Error loading CSV into table: {e}")
        return 0
#-----------------------------------------------------
#load the data from csv to table
def load_all_csv_data(conn):
    csv_files = {
        "cyber_incidents": "../DATA/cyber_incidents.csv", 
        "it_tickets": "../DATA/it_tickets.csv",
        "datasets_metadata": "../DATA/datasets_metadata.csv"
    }

    total = 0
    for table, path in csv_files.items():
        print(f"Loading {path} into {table}...")
        total += load_csv_to_table(conn, path, table)

    print(f"\nTotal rows loaded: {total}")
    return total

#-----------------------------------------------------
# Read  table
def read_all(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    return rows


def read_by_id(conn, table_name, row_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE id=?", (row_id,))
    return cursor.fetchone()

#-----------------------------------------------------
# Update table
def update_value(conn, table_name, column, new_value, row_id):
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE {table_name} SET {column}=? WHERE id=?",
        (new_value, row_id)
    )
    conn.commit()
    return cursor.rowcount

#-----------------------------------------------------
# Delete  row
def delete_row(conn, table_name, row_id):
    cursor = conn.cursor()
    cursor.execute(
        f"DELETE FROM {table_name} WHERE id=?",
        (row_id,)
    )
    conn.commit()
    return cursor.rowcount