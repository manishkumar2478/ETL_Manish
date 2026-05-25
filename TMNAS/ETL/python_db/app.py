from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2 import Error
import pandas as pd
import os
from dotenv import load_dotenv
import json
from datetime import datetime, date
from decimal import Decimal

# Load environment variables
load_dotenv()

app = Flask(__name__)

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
        return connection
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def get_tables(connection, schema_name='bse'):
    """
    Get all tables from a specific schema
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s
            ORDER BY table_name;
        """, (schema_name,))
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables
    except Error as e:
        print(f"Error getting tables: {e}")
        return []

def extract_table_data(connection, table_name, limit=100, schema_name='bse'):
    """
    Extract data from a specific table
    """
    try:
        cursor = connection.cursor()
        full_table_name = f"{schema_name}.{table_name}"
        query = f"SELECT * FROM {full_table_name} LIMIT {limit};"
        cursor.execute(query)
        
        column_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        df = pd.DataFrame(rows, columns=column_names)
        cursor.close()
        return df
    except Error as e:
        print(f"Error extracting data from table '{table_name}': {e}")
        return None

def create_audit_table(connection, schema_name='bse'):
    """
    Create audit table if it doesn't exist
    """
    try:
        cursor = connection.cursor()
        full_table_name = f"{schema_name}.audit_log"
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {full_table_name} (
                audit_id SERIAL PRIMARY KEY,
                table_name VARCHAR(255) NOT NULL,
                record_id VARCHAR(255) NOT NULL,
                operation VARCHAR(50) NOT NULL,
                old_data JSONB,
                new_data JSONB,
                updated_by VARCHAR(255) DEFAULT 'system',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        connection.commit()
        cursor.close()
        print(f"Audit table created/verified in schema '{schema_name}'")
    except Error as e:
        print(f"Error creating audit table: {e}")

def convert_decimal_to_str(obj):
    """
    Convert Decimal and date objects to strings for JSON serialization
    """
    if isinstance(obj, dict):
        return {k: convert_decimal_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_str(item) for item in obj]
    elif isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj

def log_audit(connection, table_name, record_id, operation, old_data, new_data, schema_name='bse'):
    """
    Log an audit record
    """
    try:
        cursor = connection.cursor()
        full_table_name = f"{schema_name}.audit_log"
        cursor.execute(f"""
            INSERT INTO {full_table_name} 
            (table_name, record_id, operation, old_data, new_data, updated_by, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (table_name, str(record_id), operation, 
              json.dumps(convert_decimal_to_str(old_data)) if old_data else None,
              json.dumps(convert_decimal_to_str(new_data)) if new_data else None,
              'system', datetime.now()))
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error logging audit: {e}")

def get_primary_key(connection, table_name, schema_name='bse'):
    """
    Get the primary key column names for a table (handles composite keys)
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_schema = %s
                AND tc.table_name = %s
            ORDER BY kcu.ordinal_position;
        """, (schema_name, table_name))
        results = cursor.fetchall()
        cursor.close()
        return [row[0] for row in results] if results else None
    except Error as e:
        print(f"Error getting primary key: {e}")
        return None

@app.route('/')
def index():
    """
    Home page - list all available tables
    """
    conn = connect_to_postgres()
    if conn:
        try:
            # Create audit table if it doesn't exist
            create_audit_table(conn, 'bse')
            tables = get_tables(conn, 'bse')
            return render_template('index.html', tables=tables)
        finally:
            conn.close()
    return "Error connecting to database", 500

@app.route('/table/<table_name>')
def view_table(table_name):
    """
    View data from a specific table
    """
    limit = request.args.get('limit', 100, type=int)
    conn = connect_to_postgres()
    if conn:
        try:
            df = extract_table_data(conn, table_name, limit=limit, schema_name='bse')
            if df is not None and not df.empty:
                columns = df.columns.tolist()
                data = df.values.tolist()
                pk_columns = get_primary_key(conn, table_name, 'bse')
                
                # Build record_ids for each row (composite PK support)
                record_ids = []
                if pk_columns:
                    pk_indices = [columns.index(pk) for pk in pk_columns]
                    for row in data:
                        pk_values = [str(row[idx]) for idx in pk_indices]
                        record_ids.append('|'.join(pk_values))
                else:
                    record_ids = list(range(1, len(data) + 1))
                
                return render_template('table.html', 
                                     table_name=table_name, 
                                     columns=columns, 
                                     data=data,
                                     limit=limit,
                                     row_count=len(data),
                                     pk_columns=pk_columns,
                                     record_ids=record_ids)
            else:
                return f"No data found in table '{table_name}'", 404
        finally:
            conn.close()
    return "Error connecting to database", 500

@app.route('/api/get_record/<table_name>/<record_id>')
def get_record(table_name, record_id):
    """
    Get a specific record for editing
    """
    conn = connect_to_postgres()
    if conn:
        try:
            pk_columns = get_primary_key(conn, table_name, 'bse')
            if not pk_columns:
                return jsonify({'error': 'No primary key found'}), 400
            
            cursor = conn.cursor()
            full_table_name = f"bse.{table_name}"
            
            # Parse record_id (could be composite, format: "value1|value2|value3")
            pk_values = record_id.split('|')
            
            # Build WHERE clause for composite key
            where_conditions = ' AND '.join([f"{pk} = %s" for pk in pk_columns])
            
            cursor.execute(f"""
                SELECT * FROM {full_table_name} 
                WHERE {where_conditions};
            """, pk_values)
            
            column_names = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                record = dict(zip(column_names, row))
                return jsonify({'success': True, 'record': record, 'pk_columns': pk_columns})
            else:
                return jsonify({'error': 'Record not found'}), 404
        finally:
            conn.close()
    return jsonify({'error': 'Database connection error'}), 500

@app.route('/api/update_record/<table_name>', methods=['POST'])
def update_record(table_name):
    """
    Update a record and log to audit table
    """
    data = request.json
    record_id = data.get('record_id')
    updates = data.get('updates')
    
    if not record_id or not updates:
        return jsonify({'error': 'Missing required data'}), 400
    
    conn = connect_to_postgres()
    if conn:
        try:
            pk_columns = get_primary_key(conn, table_name, 'bse')
            if not pk_columns:
                return jsonify({'error': 'No primary key found'}), 400
            
            # Parse record_id (could be composite, format: "value1|value2|value3")
            pk_values = record_id.split('|')
            
            # Get old data for audit
            cursor = conn.cursor()
            full_table_name = f"bse.{table_name}"
            
            # Build WHERE clause for composite key
            where_conditions = ' AND '.join([f"{pk} = %s" for pk in pk_columns])
            
            cursor.execute(f"""
                SELECT * FROM {full_table_name} 
                WHERE {where_conditions};
            """, pk_values)
            
            column_names = [desc[0] for desc in cursor.description]
            old_row = cursor.fetchone()
            old_data = dict(zip(column_names, old_row)) if old_row else None
            
            # Build update query (exclude PK columns from updates)
            update_columns = [k for k in updates.keys() if k not in pk_columns]
            if not update_columns:
                return jsonify({'error': 'No columns to update'}), 400
            
            set_clause = ', '.join([f"{key} = %s" for key in update_columns])
            values = [updates[key] for key in update_columns]
            values.extend(pk_values)
            
            cursor.execute(f"""
                UPDATE {full_table_name} 
                SET {set_clause} 
                WHERE {where_conditions};
            """, values)
            
            # Get new data for audit
            cursor.execute(f"""
                SELECT * FROM {full_table_name} 
                WHERE {where_conditions};
            """, pk_values)
            new_row = cursor.fetchone()
            new_data = dict(zip(column_names, new_row)) if new_row else None
            
            conn.commit()
            cursor.close()
            
            # Log to audit table
            log_audit(conn, table_name, record_id, 'UPDATE', old_data, new_data, 'bse')
            
            return jsonify({'success': True, 'message': 'Record updated successfully'})
        except Error as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
    return jsonify({'error': 'Database connection error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
