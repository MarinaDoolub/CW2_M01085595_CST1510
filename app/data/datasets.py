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
