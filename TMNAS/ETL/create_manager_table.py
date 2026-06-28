"""Create the Manager table in the bse schema."""

import logging
from postgres_connector import create_connection

# Configure logging
logger = logging.getLogger(__name__)


def create_manager_table(conn, schema_name='bse'):
    """Create the bse.manager table."""
    cursor = conn.cursor()
    try:
        # Use parameterized query for schema and table names
        cursor.execute(f"""
        CREATE SCHEMA IF NOT EXISTS {schema_name};

        CREATE TABLE IF NOT EXISTS {schema_name}.manager (
            manager_id     SERIAL       PRIMARY KEY,
            manager_name   VARCHAR(255) NOT NULL,
            employee_count INTEGER      NOT NULL DEFAULT 0,
            created_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            updated_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        logger.info(f"Table {schema_name}.manager created successfully")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating table: {e}")
        return False
    finally:
        cursor.close()


if __name__ == "__main__":
    # Connection uses environment variables automatically
    conn = create_connection()

    if conn:
        if create_manager_table(conn):
            conn.close()
            logger.info("Connection closed")
        else:
            logger.error("Failed to create manager table")
            conn.close()
    else:
        logger.error("Failed to connect to database")
