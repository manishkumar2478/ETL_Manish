import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_to_postgres():
    """
    Connect to PostgreSQL database
    """
    connection = None
    try:
        # Database connection parameters
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        print("Successfully connected to PostgreSQL database")
        return connection
        
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def test_connection(connection):
    """
    Test the database connection by querying PostgreSQL version
    """
    if connection is None:
        print("No active connection")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"PostgreSQL database version: {db_version[0]}")
        cursor.close()
    except Error as e:
        print(f"Error executing query: {e}")

def list_databases(connection):
    """
    List all databases in PostgreSQL
    """
    if connection is None:
        print("No active connection")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cursor.fetchall()
        print("\nAvailable databases:")
        for db in databases:
            print(f"  - {db[0]}")
        cursor.close()
    except Error as e:
        print(f"Error listing databases: {e}")

def list_tables(connection, database_name):
    """
    List all tables in a specific database
    """
    if connection is None:
        print("No active connection")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"\nTables in database '{database_name}':")
        for table in tables:
            print(f"  - {table[0]}")
        cursor.close()
    except Error as e:
        print(f"Error listing tables: {e}")

if __name__ == "__main__":
    # Connect to database
    conn = connect_to_postgres()
    
    if conn:
        # Test connection
        test_connection(conn)
        
        # List databases
        list_databases(conn)
        
        # List tables in current database
        current_db = os.getenv('DB_NAME', 'postgres')
        list_tables(conn, current_db)
        
        # Close connection
        conn.close()
        print("\nDatabase connection closed")
