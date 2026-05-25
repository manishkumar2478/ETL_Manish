import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Sample data
first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Lisa', 'William', 'Emma',
               'James', 'Olivia', 'Benjamin', 'Sophia', 'Lucas', 'Isabella', 'Henry', 'Mia', 'Alexander', 'Charlotte',
               'Daniel', 'Amelia', 'Matthew', 'Harper', 'Joseph', 'Evelyn', 'Samuel', 'Abigail', 'Sebastian', 'Elizabeth',
               'Ryan', 'Sofia', 'Nathan', 'Avery', 'Caleb', 'Ella', 'Dylan', 'Scarlett', 'Luke', 'Grace',
               'Isaac', 'Lily', 'Gabriel', 'Aria', 'Owen', 'Penelope', 'Carter', 'Layla', 'Julian', 'Mila',
               'Levi', 'Camila', 'Isaiah', 'Aubrey', 'Jayden', 'Hannah', 'Christopher', 'Stella', 'Lincoln', 'Nora',
               'Maverick', 'Riley', 'Ezra', 'Zoey', 'Hudson', 'Hazel', 'Jack', 'Nova', 'Elias', 'Leah',
               'Landon', 'Willow', 'Asher', 'Lucy', 'Grayson', 'Paisley', 'Wyatt', 'Savannah', 'Charles', 'Brooklyn',
               'Thomas', 'Bella', 'Miles', 'Claire', 'Samuel', 'Skylar', 'Adam', 'Violet', 'Eli', 'Ivy']

last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
              'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
              'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
              'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
              'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts']

departments = ['Engineering', 'Marketing', 'Sales', 'Human Resources', 'Finance', 'Operations', 'IT', 'Legal', 'Customer Service', 'Research']

positions = ['Manager', 'Senior Developer', 'Developer', 'Analyst', 'Specialist', 'Coordinator', 'Director', 'Associate', 'Lead', 'Assistant']

def populate_employee_table():
    """
    Populate Employee table with 100 records
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
        
        # Clear existing data
        print("Clearing existing data...")
        cursor.execute("DELETE FROM bse.Employee;")
        cursor.execute("ALTER SEQUENCE bse.Employee_EmployeeID_seq RESTART WITH 1;")
        connection.commit()
        
        # Insert 100 employees
        print("Inserting 100 employees...")
        employees = []
        
        # First, create 10 top-level managers (no manager ID)
        for i in range(10):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}@company.com"
            department = random.choice(departments)
            position = random.choice(positions)
            hire_date = datetime.now() - timedelta(days=random.randint(365, 3650))
            salary = round(random.uniform(80000, 150000), 2)
            
            employees.append([first_name, last_name, email, department, position, hire_date, salary, None])
        
        # Insert the managers first
        for emp in employees[:10]:
            cursor.execute("""
                INSERT INTO bse.Employee (FirstName, LastName, Email, Department, Position, HireDate, Salary, ManagerID)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING EmployeeID;
            """, emp)
            manager_id = cursor.fetchone()[0]
            emp[7] = manager_id  # Store the generated EmployeeID
        
        # Now insert 90 more employees with manager IDs
        for i in range(90):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{i+1}@company.com"
            department = random.choice(departments)
            position = random.choice(positions)
            hire_date = datetime.now() - timedelta(days=random.randint(30, 1825))
            salary = round(random.uniform(40000, 120000), 2)
            
            # Randomly assign a manager from the first 10 employees
            manager_id = random.choice(employees[:10])[7]
            
            cursor.execute("""
                INSERT INTO bse.Employee (FirstName, LastName, Email, Department, Position, HireDate, Salary, ManagerID)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (first_name, last_name, email, department, position, hire_date, salary, manager_id))
        
        connection.commit()
        print("100 employees inserted successfully!")
        
        # Verify the count
        cursor.execute("SELECT COUNT(*) FROM bse.Employee;")
        count = cursor.fetchone()[0]
        print(f"Total employees in table: {count}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error populating Employee table: {e}")
        if connection:
            connection.rollback()
            connection.close()

if __name__ == "__main__":
    populate_employee_table()
