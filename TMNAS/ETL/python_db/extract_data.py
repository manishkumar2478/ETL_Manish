import psycopg2
from psycopg2 import Error
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def connect_to_postgres(database_name='BSENSE'):
    """
    Connect to PostgreSQL database
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=database_name,
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Admin@123')
        )
        print(f"Successfully connected to PostgreSQL database: {database_name}")
        return connection
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def extract_table_data(connection, table_name, limit=None, schema_name='public'):
    """
    Extract data from a specific table
    
    Args:
        connection: PostgreSQL connection object
        table_name: Name of the table to extract data from
        limit: Optional limit on number of rows to extract
        schema_name: Schema name (default: public)
    
    Returns:
        DataFrame containing the table data
    """
    if connection is None:
        print("No active connection")
        return None
    
    try:
        cursor = connection.cursor()
        
        # Build query with optional limit and schema
        full_table_name = f"{schema_name}.{table_name}"
        if limit:
            query = f"SELECT * FROM {full_table_name} LIMIT {limit};"
        else:
            query = f"SELECT * FROM {full_table_name};"
        
        cursor.execute(query)
        
        # Get column names
        column_names = [desc[0] for desc in cursor.description]
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=column_names)
        
        print(f"\nExtracted {len(df)} rows from table '{full_table_name}'")
        print(f"Columns: {', '.join(column_names)}")
        
        cursor.close()
        return df
        
    except Error as e:
        print(f"Error extracting data from table '{full_table_name}': {e}")
        return None

def extract_custom_query(connection, query):
    """
    Execute a custom SQL query and return results as DataFrame
    
    Args:
        connection: PostgreSQL connection object
        query: Custom SQL query string
    
    Returns:
        DataFrame containing the query results
    """
    if connection is None:
        print("No active connection")
        return None
    
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        
        # Get column names
        column_names = [desc[0] for desc in cursor.description]
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=column_names)
        
        print(f"\nQuery executed successfully. Retrieved {len(df)} rows")
        print(f"Columns: {', '.join(column_names)}")
        
        cursor.close()
        return df
        
    except Error as e:
        print(f"Error executing custom query: {e}")
        return None

def save_to_csv(df, filename):
    """
    Save DataFrame to CSV file
    
    Args:
        df: DataFrame to save
        filename: Output filename
    """
    try:
        df.to_csv(filename, index=False)
        print(f"\nData saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def get_table_schema(connection, table_name):
    """
    Get schema information for a specific table
    
    Args:
        connection: PostgreSQL connection object
        table_name: Name of the table
    """
    if connection is None:
        print("No active connection")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        print(f"\nSchema for table '{table_name}':")
        print("-" * 80)
        print(f"{'Column Name':<30} {'Data Type':<20} {'Nullable':<10} {'Default':<20}")
        print("-" * 80)
        
        for col in columns:
            print(f"{col[0]:<30} {col[1]:<20} {col[2]:<10} {str(col[3] or ''):<20}")
        
        cursor.close()
        
    except Error as e:
        print(f"Error getting table schema: {e}")

if __name__ == "__main__":
    # Connect to BSENSE database
    conn = connect_to_postgres('BSENSE')
    
    if conn:
        try:
            # Extract data from share_detail table in bse schema
            table_name = "share_detail"
            schema_name = "bse"
            
            # Extract data (limit to 10 rows)
            df = extract_table_data(conn, table_name, limit=10, schema_name=schema_name)
            
            if df is not None and not df.empty:
                print("\nPreview of data:")
                print(df.head())
                
                # Save to CSV in Output directory
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = "Output"
                filename = f"{output_dir}/share_detail_{timestamp}.csv"
                save_to_csv(df, filename)
                print(f"\nData saved to: {filename}")
            else:
                print("No data found in the table")
        
        finally:
            conn.close()
            print("\nDatabase connection closed")
