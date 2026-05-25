"""Create the Manager table in the bse schema."""

from postgres_connector import create_connection


DDL = """
CREATE SCHEMA IF NOT EXISTS bse;

CREATE TABLE IF NOT EXISTS bse.manager (
    manager_id     SERIAL       PRIMARY KEY,
    manager_name   VARCHAR(255) NOT NULL,
    employee_count INTEGER      NOT NULL DEFAULT 0
);
"""


def create_manager_table(conn):
    """Create the bse.manager table."""
    cursor = conn.cursor()
    try:
        cursor.execute(DDL)
        conn.commit()
        print("Table bse.manager created successfully")
    except Exception as e:
        conn.rollback()
        print(f"Error creating table: {e}")
    finally:
        cursor.close()


if __name__ == "__main__":
    # Update these with your database credentials
    conn = create_connection(
        host="localhost",
        port="5432",
        database="your_database",
        user="your_username",
        password="your_password",
    )

    if conn:
        create_manager_table(conn)
        conn.close()
        print("Connection closed")
