import pandas as pd
from app.data.db import connect_database

#-________________________________________________________________________-
#Inserting a new cyber incident into the database.

def insert_incident(conn, date, incident_type, severity, status, description, reported_by=None):

    cursor = conn.cursor()

    # Set default reporter if none provided
    if reported_by is None:
        reported_by = 'system'
        
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