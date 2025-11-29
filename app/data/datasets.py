import pandas as pd
from app.data.db import connect_database

#-________________________________________________________________________-
#Inserting a new dataset into the database.

def insert_dataset(conn, dataset_name,rows,columns,uploaded_by ,upload_date):
    cursor = conn.cursor()
    
    cursor.execute ("""
        INSERT INTO datasets_metadata
        (dataset_name,rows,columns,uploaded_by ,upload_date)
        VALUES (?, ?, ?, ?, ?, ?,?,?)
         """,(dataset_name,rows,columns,uploaded_by ,upload_date))

    conn.commit()

    # Return the ID of the inserted row
    return cursor.lastrowid

#Retrieving all datasets from the database.

def get_all_datasets(conn):

    try:
        # Using pandas to read directly from the connection
        df = pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY dataset_id DESC", conn)
        print(f" Retrieved {len(df)} datasets from the database")
        return df
    except Exception as e:
        print(f" Error retrieving datasets: {e}")
        return pd.DataFrame()  # return empty DataFrame on error

#-________________________________________________________________________-

#Updating the category of a dataset.

def update_dataset(conn, dataset_id, category):
    
    cursor = conn.cursor()
    cursor.execute("""UPDATE datasets_metadata SET category = ? WHERE dataset_id = ?""",(category, dataset_id))

    conn.commit()

    # Return number of rows affected
    return cursor.rowcount
#-________________________________________________________________________-

#Delete a dataset from the database.

def delete_dataset(conn, dataset_id):

    cursor = conn.cursor()
    cursor.execute ("""DELETE FROM datasets_metadata WHERE dataset_id = ?""", (dataset_id,))

    conn.commit()

    return cursor.rowcount

# Analytical reporting queries
#-________________________________________________________________________-
#this analyses the resource consumption
def get_largest_datasets(conn):
    query = """
    SELECT dataset_name, rows, columns
    FROM datasets_metadata
    ORDER BY rows DESC
    LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    return df

#-________________________________________________________________________-
#this identifies what to archive that is the oldest and largest ones
def get_archiving_candidates(conn):
    query = """
    SELECT dataset_name, rows, upload_date
    FROM datasets_metadata
    WHERE upload_date < DATE('now', '-6 months')
    ORDER BY rows DESC
    """
    df = pd.read_sql_query(query, conn)
    return df
#-________________________________________________________________________-
#to see who uploads the most data
def get_dataset_contributor_dependency(conn):
    query = """
    SELECT uploaded_by, COUNT(*) AS total_datasets
    FROM datasets_metadata
    GROUP BY uploaded_by
    ORDER BY total_datasets DESC
    """
    df = pd.read_sql_query(query, conn)
    return df