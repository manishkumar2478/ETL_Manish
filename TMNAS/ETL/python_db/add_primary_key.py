import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def remove_duplicates_and_add_pk():
    """
    Remove duplicate records and add composite primary key to share_detail table
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
        
        # First, check if primary key already exists
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_schema = 'bse'
            AND table_name = 'share_detail'
            AND constraint_type = 'PRIMARY KEY';
        """)
        
        existing_pk = cursor.fetchone()
        
        if existing_pk:
            print(f"Primary key already exists: {existing_pk[0]}")
            print("Dropping existing primary key...")
            cursor.execute(f"""
                ALTER TABLE bse.share_detail
                DROP CONSTRAINT {existing_pk[0]};
            """)
            connection.commit()
            print("Existing primary key dropped.")
        
        # Check for duplicates
        print("Checking for duplicate records...")
        cursor.execute("""
            SELECT ticker, load_date, COUNT(*) as count
            FROM bse.share_detail
            GROUP BY ticker, load_date
            HAVING COUNT(*) > 1
            ORDER BY count DESC;
        """)
        
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"Found {len(duplicates)} duplicate (ticker, load_date) combinations:")
            for dup in duplicates:
                print(f"  - {dup[0]}, {dup[1]}: {dup[2]} records")
            
            # Remove duplicates by keeping only the first occurrence for each (ticker, load_date)
            print("\nRemoving duplicates (keeping first occurrence)...")
            cursor.execute("""
                DELETE FROM bse.share_detail
                WHERE ctid NOT IN (
                    SELECT MIN(ctid)
                    FROM bse.share_detail
                    GROUP BY ticker, load_date
                );
            """)
            deleted_count = cursor.rowcount
            connection.commit()
            print(f"Deleted {deleted_count} duplicate records.")
        else:
            print("No duplicates found.")
        
        # Add composite primary key on ticker and load_date
        print("\nAdding composite primary key on (ticker, load_date)...")
        cursor.execute("""
            ALTER TABLE bse.share_detail
            ADD CONSTRAINT pk_share_detail PRIMARY KEY (ticker, load_date);
        """)
        
        connection.commit()
        print("Primary key added successfully!")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error: {e}")
        if connection:
            connection.rollback()
            connection.close()

if __name__ == "__main__":
    remove_duplicates_and_add_pk()
