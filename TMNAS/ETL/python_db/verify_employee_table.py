import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_employee_table():
    """
    Verify Employee table data
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'BSENSE'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Admin@123')
        )
        
        cursor = connection.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM bse.Employee;")
        total_count = cursor.fetchone()[0]
        print(f"Total employees: {total_count}")
        
        # Get count of employees with managers
        cursor.execute("SELECT COUNT(*) FROM bse.Employee WHERE ManagerID IS NOT NULL;")
        with_manager = cursor.fetchone()[0]
        print(f"Employees with ManagerID: {with_manager}")
        
        # Get count of employees without managers (top-level)
        cursor.execute("SELECT COUNT(*) FROM bse.Employee WHERE ManagerID IS NULL;")
        without_manager = cursor.fetchone()[0]
        print(f"Employees without ManagerID (top-level): {without_manager}")
        
        # Show sample records
        print("\nSample records (first 10):")
        print("-" * 100)
        cursor.execute("""
            SELECT EmployeeID, FirstName, LastName, Email, Department, Position, ManagerID
            FROM bse.Employee
            ORDER BY EmployeeID
            LIMIT 10;
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]} {row[2]}, Dept: {row[4]}, Position: {row[5]}, ManagerID: {row[6]}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error verifying Employee table: {e}")
        if connection:
            connection.close()

if __name__ == "__main__":
    verify_employee_table()
