import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_employee_table():
    """
    Create Employee table in bse schema
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
        
        # Create Employee table
        print("Creating Employee table in bse schema...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bse.Employee (
                EmployeeID SERIAL PRIMARY KEY,
                FirstName VARCHAR(50) NOT NULL,
                LastName VARCHAR(50) NOT NULL,
                Email VARCHAR(100) UNIQUE NOT NULL,
                Department VARCHAR(50),
                Position VARCHAR(50),
                HireDate DATE DEFAULT CURRENT_DATE,
                Salary DECIMAL(10, 2),
                ManagerID INTEGER REFERENCES bse.Employee(EmployeeID)
            );
        """)
        
        connection.commit()
        print("Employee table created successfully!")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error creating Employee table: {e}")
        if connection:
            connection.close()

if __name__ == "__main__":
    create_employee_table()
