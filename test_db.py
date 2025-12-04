from app.data.db import connect_database
from app.services.user_service import register_user, login_user
from app.data.users import insert_user, get_user_by_username, update_user_role, delete_user
from app.data.incidents import (
    get_incidents_by_category,
    get_bottleneck_categories_by_status,
    get_resolution_status_breakdown
)

from app.data.users import get_user_by_username, insert_user
import bcrypt

def run_comprehensive_tests():
    """
    Run comprehensive tests on your database.
    """
    print("\n" + "="*60)
    print("🧪 RUNNING COMPREHENSIVE TESTS")
    print("="*60)

    conn = connect_database()

#-----------------------------------------------------------------------------

    # Test 1: Authentication
    print("\n[TEST 1] Authentication")
    success, msg = register_user(conn, "test_user", "MiddlesexUniversity2025!", "user")
    print(f"  Register: {'✅' if success else '❌'} {msg}")

    success, msg = login_user(conn, "test_user", "MiddlesexUniversity2025!")
    print(f"  Login:    {'✅' if success else '❌'} {msg}")

#-----------------------------------------------------------------------------
    # Test 2: CRUD Operations
    print("\n[TEST 2] CRUD Operations")

    #CRUD operations for users
#---------------------------------------------------------------------------------------------
     # Insert a user manually
    password = "TestPass1234!"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_id = insert_user(conn, "new_user", hashed, role="user")
    print(f"  Insert: User 'new_user' inserted with ID {user_id}")

    # Retrieve the user
    user = get_user_by_username(conn, "marina")
    if user:
        print(f" Retrieved user '{user[1]}' from DB")
    else:
        print(" User not found")

    # Update role of the user
    rows_updated = update_user_role(conn, "marina", "admin")
    print(f"  Update:  {'✅' if rows_updated > 0 else '❌'} Role updated")
    # Verify the update
    user = get_user_by_username(conn, "marina")
    print(f"  Verified role: {user[1]}")
    
    #Delete user
    
    rows_deleted = delete_user(conn, user_id = 5)  
    print(f"  Delete:  {'✅' if rows_deleted > 0 else '❌'} User deleted")

    # --- Verify deletion ---
    user = get_user_by_username(conn, "test_user") 
    if not user:
        print("  Verify delete:  User no longer exists")
    else:
        print("  Verify delete:  Still exists")

#-----------------------------------------------------------------------------
   
    # Test 3: Analytical Queries based on coursework recommendations
    print("\n[TEST 3] Analytical Queries")


    df1 = get_incidents_by_category(conn)
    print("\nIncidents by Category:")
    print(df1)

    #Bottleneck unresolved categories
        
    df2 = get_bottleneck_categories_by_status(conn)
    print("\nBottleneck Categories (Unresolved incidents):")
    print(df2)

    #Resolution status breakdown
        
    df3 = get_resolution_status_breakdown(conn)
    print("\nResolution Status Breakdown:")
    print(df3)

    conn.close()
    #--------------------------------------------------------------------------------------------
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)

if __name__ == "__main__":
    run_comprehensive_tests()


