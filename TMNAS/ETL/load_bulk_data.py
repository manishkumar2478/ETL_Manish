"""
Load bulk.csv data into PostgreSQL database
"""

import psycopg2
from psycopg2 import Error
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def connect_to_postgres(database_name=None):
    """
    Connect to PostgreSQL database using environment variables.
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=database_name or os.getenv('DB_NAME', 'BSENSE'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD'),
        )
        logger.info(f"Connection to PostgreSQL successful (DB: {database_name or os.getenv('DB_NAME')})")
        return connection
    except Error as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        return None


def create_stock_trades_table(connection, schema_name='bse'):
    """
    Create stock_trades table if it doesn't exist
    """
    try:
        cursor = connection.cursor()
        full_table_name = f"{schema_name}.stock_trades"
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {full_table_name} (
                trade_id SERIAL PRIMARY KEY,
                trade_date DATE NOT NULL,
                symbol VARCHAR(50) NOT NULL,
                security_name VARCHAR(255) NOT NULL,
                client_name VARCHAR(255) NOT NULL,
                buy_sell VARCHAR(10) NOT NULL CHECK (buy_sell IN ('BUY', 'SELL')),
                quantity_traded BIGINT NOT NULL,
                trade_price DECIMAL(12, 2) NOT NULL,
                remarks VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_trade UNIQUE (trade_date, symbol, client_name, buy_sell, quantity_traded)
            );
        """)
        
        connection.commit()
        print(f"Table {full_table_name} created/verified successfully")
        cursor.close()
        return True
    except Error as e:
        print(f"Error creating table: {e}")
        return False


def load_bulk_csv(connection, csv_file_path, schema_name='bse'):
    """
    Load bulk.csv data into stock_trades table with comprehensive error handling.
    """
    try:
        # Read CSV file
        logger.info(f"Reading CSV file: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        
        logger.info(f"CSV file has {len(df)} rows")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Convert date format
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
        
        # Replace '-' with None for Remarks
        df['Remarks'] = df['Remarks'].replace('-', None)
        
        # Connect to database
        cursor = connection.cursor()
        full_table_name = f"{schema_name}.stock_trades"
        
        # Insert data
        insert_count = 0
        duplicate_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                cursor.execute(f"""
                    INSERT INTO {full_table_name} 
                    (trade_date, symbol, security_name, client_name, buy_sell, 
                     quantity_traded, trade_price, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['Date'],
                    row['Symbol'],
                    row['Security Name'],
                    row['Client Name'],
                    row['Buy/Sell'],
                    int(row['Quantity Traded']),
                    float(row['Trade Price / Wght. Avg. Price']),
                    row['Remarks']
                ))
                insert_count += 1
            except Error as e:
                if 'unique_trade' in str(e) or 'unique constraint' in str(e).lower():
                    duplicate_count += 1
                    logger.debug(f"Duplicate record at row {index + 1}")
                else:
                    error_count += 1
                    logger.error(f"Row {index + 1} error: {e}")
                connection.rollback()
        
        connection.commit()
        cursor.close()
        
        logger.info(f"✓ Data loaded successfully!")
        logger.info(f"  - Inserted: {insert_count} rows")
        logger.info(f"  - Duplicates skipped: {duplicate_count} rows")
        logger.info(f"  - Errors: {error_count} rows")
        
        return True
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return False


def verify_data(connection, schema_name='bse'):
    """
    Verify loaded data with comprehensive logging.
    """
    try:
        cursor = connection.cursor()
        full_table_name = f"{schema_name}.stock_trades"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {full_table_name};")
        total_count = cursor.fetchone()[0]
        
        # Get count by buy/sell
        cursor.execute(f"""
            SELECT buy_sell, COUNT(*) as count 
            FROM {full_table_name}
            GROUP BY buy_sell;
        """)
        buy_sell_stats = cursor.fetchall()
        
        # Get unique symbols count
        cursor.execute(f"SELECT COUNT(DISTINCT symbol) FROM {full_table_name};")
        unique_symbols = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute(f"""
            SELECT trade_date, symbol, security_name, buy_sell, quantity_traded, trade_price
            FROM {full_table_name}
            LIMIT 5;
        """)
        sample_data = cursor.fetchall()
        
        cursor.close()
        
        logger.info("📊 Data Verification:")
        logger.info(f"  - Total records: {total_count}")
        logger.info(f"  - Unique symbols: {unique_symbols}")
        logger.info(f"  - Buy/Sell breakdown:")
        for action, count in buy_sell_stats:
            logger.info(f"    • {action}: {count}")
        
        logger.info(f"Sample records:")
        for row in sample_data:
            logger.info(f"    {row[0]} | {row[1]} | {row[2][:30]} | {row[3]} | {row[4]} @ {row[5]}")
        
    except Error as e:
        logger.error(f"Error verifying data: {e}")


def main():
    """
    Main function to orchestrate bulk data loading.
    """
    logger.info("=" * 60)
    logger.info("  BULK DATA LOADER - Stock Trades")
    logger.info("=" * 60)
    
    # CSV file path
    csv_file = r"c:\GithubCopilotProject\bulk.csv"
    
    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found at {csv_file}")
        return
    
    # Connect to database
    logger.info("[1/4] Connecting to PostgreSQL...")
    conn = connect_to_postgres()
    if not conn:
        logger.error("Failed to connect. Exiting.")
        return
    
    # Create table
    logger.info("[2/4] Creating stock_trades table...")
    if not create_stock_trades_table(conn):
        logger.error("Failed to create table. Exiting.")
        conn.close()
        return
    
    # Load data
    logger.info("[3/4] Loading bulk CSV data...")
    if not load_bulk_csv(conn, csv_file):
        logger.error("Failed to load data. Exiting.")
        conn.close()
        return
    
    # Verify data
    logger.info("[4/4] Verifying loaded data...")
    verify_data(conn)
    
    conn.close()
    logger.info("=" * 60)
    logger.info("  ✓ Process completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
