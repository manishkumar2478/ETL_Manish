# PostgreSQL Data Extraction with Python

Python scripts to connect to PostgreSQL database and extract data.

## Prerequisites

- Python 3.7 or higher
- PostgreSQL installed and running
- PostgreSQL database credentials

## Installation

1. Install Python dependencies:
```bash
cd C:\Users\manish\login-app\python_db
pip install -r requirements.txt
```

2. Create `.env` file with your database credentials:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

## Usage

### 1. Test Connection and List Databases

```bash
python connect_postgres.py
```

This script will:
- Connect to PostgreSQL
- Display PostgreSQL version
- List all available databases
- List tables in the current database

### 2. Extract Data from Tables

```bash
python extract_data.py
```

This script will:
- Connect to PostgreSQL
- Prompt you for a table name
- Display table schema
- Extract and preview data (first 100 rows)
- Save data to CSV file
- Option to extract all data
- Option to run custom SQL queries

## Features

- **Connection Testing**: Verify PostgreSQL connection and list databases/tables
- **Table Schema**: View column names, data types, and constraints
- **Data Extraction**: Extract data from any table with optional row limits
- **Custom Queries**: Execute custom SQL queries and export results
- **CSV Export**: Save extracted data to CSV files with timestamps
- **Pandas Integration**: Data returned as pandas DataFrames for easy manipulation

## Example Output

```
Successfully connected to PostgreSQL database
PostgreSQL database version: PostgreSQL 15.0...

Available databases:
  - postgres
  - login_db
  - template1

Tables in database 'login_db':
  - users

Schema for table 'users':
Column Name                   Data Type             Nullable    Default
--------------------------------------------------------------------------------
id                            integer               NO         
username                      character varying     NO         
email                         character varying     NO         
password                      character varying     NO         
created_at                    timestamp without ti YES        CURRENT_TIMESTAMP

Extracted 2 rows from table 'users'
Columns: id, username, email, password, created_at

Preview of data:
   id  username           email                password                     created_at
0   1  johndoe           john@example.com     $2a$10$...                    2024-01-01 00:00:00
1   2  janedoe           jane@example.com     $2a$10$...                    2024-01-02 00:00:00

Data saved to users_data_20240101_120000.csv
```

## Custom Query Examples

```sql
-- Get users created in the last 7 days
SELECT * FROM users WHERE created_at >= NOW() - INTERVAL '7 days';

-- Count users by email domain
SELECT 
    SUBSTRING(email FROM '@(.*)$') as domain,
    COUNT(*) as user_count
FROM users
GROUP BY domain
ORDER BY user_count DESC;

-- Get user statistics
SELECT 
    COUNT(*) as total_users,
    MIN(created_at) as first_user,
    MAX(created_at) as latest_user
FROM users;
```

## Troubleshooting

### Connection Errors
- Verify PostgreSQL is running
- Check credentials in `.env` file
- Ensure database exists
- Check firewall settings

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.7+ required)

### Permission Errors
- Verify user has SELECT permissions on tables
- Check database user privileges
