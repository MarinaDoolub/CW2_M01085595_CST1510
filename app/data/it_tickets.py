import pandas as pd
from app.data.db import connect_database

#-________________________________________________________________________-
#Inserting a new ticket into the database.

def insert_tickets(conn,ticket_id,priority,description,status,assigned_to,created_at,resolution_time_hours):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO it_tickets
        (ticket_id,priority,description,status,assigned_to,created_at,resolution_time_hours )
        VALUES (?,?, ?, ?, ?, ?, ?, ?)""",(ticket_id,priority,description,status,assigned_to,created_at,resolution_time_hours))
    conn.commit()

    # Return the ID of the inserted row
    return cursor.lastrowid

#-________________________________________________________________________-
#Retrieving all tickets from the database.

def get_all_tickets(conn):

    try:
        # Using pandas to read directly from the connection
        df = pd.read_sql_query("SELECT * FROM it_tickets ORDER BY ticket_id DESC", conn)
        print(f" Retrieved {len(df)} tickets from the database")
        return df
    except Exception as e:
        print(f" Error retrieving tickets: {e}")
        return pd.DataFrame()  # return empty DataFrame on error

#-________________________________________________________________________-

#Updating the status of a ticket.

def update_tickets(conn, ticket_id, new_status):

    cursor = conn.cursor()
    cursor.execute("""UPDATE it_tickets SET status = ? WHERE ticket_id = ?""", (new_status, ticket_id))

    conn.commit()

    # Return number of rows affected
    return cursor.rowcount

#-________________________________________________________________________-

#Delete ticket from the database.


def delete_ticket(conn, ticket_id):

    cursor = conn.cursor()
    cursor.execute("""DELETE FROM it_tickets WHERE ticket_id = ?""", (ticket_id,))

    conn.commit()

    return cursor.rowcount
# Analytical reporting queries
#-________________________________________________________________________-
#counting the number of tickets by the status
def get_tickets_by_status(conn):

    query = """
    SELECT status, COUNT(*) as count
    FROM it_tickets
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

#-________________________________________________________________________-
#to identify the urgency load

def count_tickets_by_priority(conn):

    query = """
    SELECT priority, COUNT(*) as count
    FROM it_tickets
    GROUP BY priority
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

#-________________________________________________________________________-
#to identify the performance 
#i)by ticket status

def slowest_resolution_by_status(conn):
    query = """
    SELECT status, AVG(resolution_time_hours) AS avg_hours
    FROM it_tickets
    WHERE resolution_time_hours > 0
    GROUP BY status
    ORDER BY avg_hours DESC
    LIMIT 5
    """
    return pd.read_sql_query(query, conn)

#ii)by which staff member who is causing the most delays
def slowest_resolution_by_staff(conn):
    query = """
    SELECT assigned_to, AVG(resolution_time_hours) AS avg_hours
    FROM it_tickets
    WHERE resolution_time_hours > 0 AND assigned_to IS NOT NULL
    GROUP BY assigned_to
    ORDER BY avg_hours DESC
    LIMIT 5
    """
    return pd.read_sql_query(query, conn)