#creating functions to create the tables
#-________________________________________________________________________-
#creating the users's table
def create_users_table(conn):

    cursor = conn.cursor()
    # SQL statement to create users table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    cursor.execute(create_table_sql)
    conn.commit()
    print("Users table created successfully!")

#-________________________________________________________________________-

#Creating Domain Tables

def create_cyber_incidents_table(conn):

    cursor = conn.cursor()

    # SQL statement to create cyber_incidents table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cyber_incidents (
    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL,
    description TEXT,
    created_by TEXT
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print("Cyber incidents table created successfully!")

#-________________________________________________________________________-
def create_datasets_metadata_table(conn):
    cursor = conn.cursor()
    # SQL statement to create  datasets_metadata_table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,   
        dataset_name TEXT NOT NULL,
        rows INTEGER,                           
        columns INTEGER,                              
        uploaded_by TEXT,                                
        upload_date TEXT                                                                                                                        
    );
    """

    cursor.execute(create_table_sql)
    conn.commit()
    print("Datasets metadata table created successfully!")
#-________________________________________________________________________-

def create_it_tickets_table(conn):
    cursor = conn.cursor()
    # SQL statement to create  it_tickets_table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS it_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,           
        ticket_id TEXT UNIQUE NOT NULL,                 
        priority TEXT,                                                                      
        description TEXT,   
        status TEXT,                            
        assigned_to TEXT,                               
        created_at TEXT,                                                         
        resolution_time_hours REAL                   
    );
    """

    cursor.execute(create_table_sql)
    conn.commit()
    print("IT tickets table created successfully!")

def create_all_tables(conn):
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)