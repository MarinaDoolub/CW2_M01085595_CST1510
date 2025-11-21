import pandas as pd
from pathlib import Path

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

def load_all_csv_data(conn):
    csv_files = {
        "cyber_incidents": "DATA/cyber_incidents.csv",
        "it_tickets": "DATA/it_tickets.csv",
        "datasets_metadata": "DATA/datasets_metadata.csv"
    }

    total = 0
    for table, path in csv_files.items():
        print(f"Loading {path} into {table}...")
        total += load_csv_to_table(conn, path, table)

    print(f"\nTotal rows loaded: {total}")
    return total
