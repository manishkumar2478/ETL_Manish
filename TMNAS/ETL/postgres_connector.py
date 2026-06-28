import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_db_config():
    """Get database configuration from environment variables."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'BSENSE'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD'),
    }


def create_connection(host=None, port=None, database=None, user=None, password=None):
    """Create a connection to a PostgreSQL database.
    
    Uses environment variables if parameters not provided.
    """
    try:
        config = get_db_config()
        conn = psycopg2.connect(
            host=host or config['host'],
            port=port or config['port'],
            database=database or config['database'],
            user=user or config['user'],
            password=password or config['password'],
        )
        logger.info(f"Connection to PostgreSQL successful (Database: {config['database']})")
        return conn
    except OperationalError as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        return None


def run_query(conn, query):
    """Execute a query and return results."""
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return None
    finally:
        cursor.close()


if __name__ == "__main__":
    # Connection uses environment variables automatically
    conn = create_connection()

    if conn:
        # Example: list all tables
        results = run_query(
            conn,
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';",
        )
        if results:
            for row in results:
                print(row)
        conn.close()
        print("Connection closed")
