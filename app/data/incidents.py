import pandas as pd
from app.data.db import connect_database

#-________________________________________________________________________-
#Inserting a new cyber incident into the database.

def insert_incident(conn, date, incident_type, severity, status, description, reported_by=None):

    cursor = conn.cursor()

    # Parameterized SQL query to prevent SQL injection
    insert_query = """
        INSERT INTO cyber_incidents
        (date, incident_type, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.execute(insert_query, (date, incident_type, severity, status, description, reported_by))
    conn.commit()

    # Return the ID of the inserted row
    return cursor.lastrowid

#-________________________________________________________________________-
#Retrieving all incidents from the database.

def get_all_incidents(conn):

    try:
        df = pd.read_sql_query("SELECT * FROM cyber_incidents ORDER BY id DESC", conn)
        print(f" Retrieved {len(df)} incidents from the database")
        return df
    except Exception as e:
        print(f" Error retrieving incidents: {e}")
        return pd.DataFrame()  # return empty DataFrame on error

#-________________________________________________________________________-
#Updating the status of an incident.

def update_incident_status(conn, incident_id, new_status):

    cursor = conn.cursor()

    # Parameterized SQL to prevent SQL injection
    update_query = "UPDATE cyber_incidents SET status = ? WHERE id = ?"
    cursor.execute(update_query, (new_status, incident_id))

    conn.commit()

    # Return number of rows affected
    return cursor.rowcount

#-________________________________________________________________________-
#Delete an incident from the database.


def delete_incident(conn, incident_id):

    cursor = conn.cursor()

    delete_query = "DELETE FROM cyber_incidents WHERE id = ?"
    cursor.execute(delete_query, (incident_id,))

    conn.commit()

    return cursor.rowcount

#-________________________________________________________________________-
#Counting incidents by type.

def get_incidents_by_type_count(conn):

    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

#-________________________________________________________________________-
#Counting high severity incidents by status.

def get_high_severity_by_status(conn):

    query = """
    SELECT status, COUNT(*) as count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

#-________________________________________________________________________-
#Finding incident types above a minimum count.

def get_incident_types_with_many_cases(conn, min_count=5):

    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df