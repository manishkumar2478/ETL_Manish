import psycopg2
from psycopg2 import OperationalError


def create_connection(host, port, database, user, password):
    """Create a connection to a PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )
        print("Connection to PostgreSQL successful")
        return conn
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None


def run_query(conn, query):
    """Execute a query and return results."""
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        cursor.close()


if __name__ == "__main__":
    # Update these with your database credentials
    conn = create_connection(
        host="localhost",
        port="5432",
        database="BSENSE",
        user="postgres",
        password="Admin@123",
    )


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
