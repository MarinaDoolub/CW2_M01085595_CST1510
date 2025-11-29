import pandas as pd
from app.data.db import connect_database

#-________________________________________________________________________-
#Inserting a new cyber incident into the database.
def insert_incident(conn,timestamp, severity, category, status, description,created_by):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cyber_incidents
        (timestamp, severity, category, status, description,created_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """,(timestamp,severity, category, status, description,created_by))
    conn.commit()

    # Return the ID of the inserted row
    return cursor.lastrowid

#-________________________________________________________________________-
#Retrieving all incidents from the database.

def get_all_incidents(conn):

    try:
        # Using pandas to read directly from the connection
        df = pd.read_sql_query("SELECT * FROM cyber_incidents ORDER BY incident_id DESC", conn)
        print(f" Retrieved {len(df)} incidents from the database")
        return df
    except Exception as e:
        print(f" Error retrieving incidents: {e}")
        return pd.DataFrame()  # return empty DataFrame on error

#-________________________________________________________________________-

#Updating the status of an incident.

def update_incident_status(conn, incident_id, new_status):

    cursor = conn.cursor()
    cursor.execute("""UPDATE cyber_incidents SET status = ? WHERE incident_id = ?""",(new_status, incident_id))
    conn.commit()

    # Return number of rows affected
    return cursor.rowcount

#-________________________________________________________________________-

#Delete an incident from the database.

def delete_incident(conn, incident_id):

    cursor = conn.cursor()

    cursor.execute("""DELETE FROM cyber_incidents WHERE incident_id = ?""",(incident_id,))
    conn.commit()

    return cursor.rowcount

# Analytical reporting queries
#-________________________________________________________________________-
#this gets total incidents by category and shows the trend 

def get_incidents_by_category(conn):
    query = """
    SELECT category, COUNT(*) AS count
    FROM cyber_incidents
    GROUP BY category
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

#-________________________________________________________________________-
#this identifies the bottleneck categories by the unresolved incidents

def get_bottleneck_categories_by_status(conn):
    query = """
    SELECT category, COUNT(*) AS unresolved_count
    FROM cyber_incidents
    WHERE status NOT IN ('Resolved', 'Closed')
    GROUP BY category
    ORDER BY unresolved_count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df
#-________________________________________________________________________-
#this will show the resolution perfomance that is a detailed view of the open vs the closed statuses

def get_resolution_status_breakdown(conn):
    query = """
    SELECT category, status, COUNT(*) AS count
    FROM cyber_incidents
    GROUP BY category, status
    ORDER BY category, count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df