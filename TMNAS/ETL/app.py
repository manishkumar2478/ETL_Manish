"""ETL application: connects to PostgreSQL, sets up tables, and demonstrates CRUD operations."""

import sys

from postgres_connector import create_connection, run_query
from create_manager_table import create_manager_table


DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "etl_db",
    "user": "etl_user",
    "password": "etl_password",
}

SAMPLE_MANAGERS = [
    ("Alice Johnson", 12),
    ("Bob Smith", 8),
    ("Carol Williams", 15),
    ("David Brown", 5),
    ("Eva Martinez", 10),
]


def insert_sample_data(conn):
    """Insert sample manager records if the table is empty."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM bse.manager;")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Table bse.manager already has {count} rows — skipping insert")
            return

        for name, emp_count in SAMPLE_MANAGERS:
            cursor.execute(
                "INSERT INTO bse.manager (manager_name, employee_count) VALUES (%s, %s);",
                (name, emp_count),
            )
        conn.commit()
        print(f"Inserted {len(SAMPLE_MANAGERS)} sample managers")
    except Exception as e:
        conn.rollback()
        print(f"Error inserting sample data: {e}")
    finally:
        cursor.close()


def display_managers(conn):
    """Query and display all managers."""
    results = run_query(conn, "SELECT manager_id, manager_name, employee_count FROM bse.manager ORDER BY manager_id;")
    if results:
        print(f"\n{'ID':<5} {'Manager Name':<20} {'Employees':<10}")
        print("-" * 35)
        for row in results:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<10}")
        print(f"\nTotal managers: {len(results)}")
    else:
        print("No managers found")


def main():
    print("=" * 50)
    print("  ETL Application — Manager Database")
    print("=" * 50)

    print("\n[1/4] Connecting to PostgreSQL...")
    conn = create_connection(**DB_CONFIG)
    if not conn:
        print("Failed to connect. Exiting.")
        sys.exit(1)

    print("\n[2/4] Creating bse.manager table...")
    create_manager_table(conn)

    print("\n[3/4] Inserting sample data...")
    insert_sample_data(conn)

    print("\n[4/4] Querying managers...")
    display_managers(conn)

    conn.close()
    print("\nConnection closed. Done!")


if __name__ == "__main__":
    main()
