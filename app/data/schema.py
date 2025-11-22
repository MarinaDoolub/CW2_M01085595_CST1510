# #creating functions to create the tables
# #-________________________________________________________________________-
# #creating the users's table
# def create_users_table(conn):

#     cursor = conn.cursor()


#     # SQL statement to create users table
#     create_table_sql = """
#     CREATE TABLE IF NOT EXISTS users (
#         user_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT NOT NULL UNIQUE,
#         password_hash TEXT NOT NULL,
#         role TEXT DEFAULT 'user',
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
#     """

#     cursor.execute(create_table_sql)
#     conn.commit()
#     print("Users table created successfully!")

# #-________________________________________________________________________-

#Creating Domain Tables

def create_cyber_incidents_table(conn):

    cursor = conn.cursor()

    # SQL statement to create cyber_incidents table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DEFAULT CURRENT_TIMESTAMP,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        description TEXT,
        reported_by TEXT NOT NULL,
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print("Cyber incidents table created successfully!")

#-________________________________________________________________________-