# ETL_Manish

## 🔒 Security Updates

This project has been updated with important security fixes:
- ✅ Removed hardcoded database credentials
- ✅ Fixed SQL injection vulnerabilities
- ✅ Added input validation
- ✅ Implemented comprehensive logging
- ✅ Added unit tests

**See [SECURITY.md](SECURITY.md) for detailed information.**

## Quick Start

### 1. Setup Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your database credentials
# DO NOT commit .env to version control
```

### 2. Install Dependencies

```bash
pip install -r TMNAS/ETL/requirements.txt
```

### 3. Run ETL Scripts

All scripts now use environment variables from `.env` automatically.

## TMNAS / ETL

### PostgreSQL Connector

A Python utility for connecting to PostgreSQL databases and executing queries.

**Features:**
- Auto-loads credentials from `.env` environment variables
- Comprehensive error handling and logging
- Connection pooling support

**Usage:**

```bash
python TMNAS/ETL/postgres_connector.py
```

The script will automatically use credentials from `.env`.

### Manager Table (bse schema)

Creates the `bse.manager` table with the following columns:

| Column         | Type         | Description                          |
|----------------|--------------|--------------------------------------|
| manager_id     | SERIAL (PK)  | Auto-incrementing manager identifier |
| manager_name   | VARCHAR(255) | Name of the manager                  |
| employee_count | INTEGER      | Number of employees under the manager|
| created_at     | TIMESTAMP    | Record creation timestamp            |
| updated_at     | TIMESTAMP    | Record update timestamp              |

**Usage:**

```bash
python TMNAS/ETL/create_manager_table.py
```

The script will:
1. Create the `bse` schema if it doesn't exist
2. Create the manager table with all columns
3. Log the operation with timestamps

Alternatively, execute the raw SQL directly:

```bash
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f TMNAS/ETL/sql/create_manager_table.sql
```

### Bulk Data Loader

Load stock trading data from CSV files into the database.

**Features:**
- Automatic table creation
- Duplicate detection
- Data validation
- Comprehensive verification
- Error logging

**Usage:**

```bash
python TMNAS/ETL/load_bulk_data.py
```

**Output:**
```
============================================================
  BULK DATA LOADER - Stock Trades
============================================================

[1/4] Connecting to PostgreSQL...
Connection to PostgreSQL successful

[2/4] Creating stock_trades table...
Table bse.stock_trades created/verified successfully

[3/4] Loading bulk CSV data...
✓ Data loaded successfully!
  - Inserted: 222 rows
  - Duplicates skipped: 0 rows
  - Errors: 0 rows

[4/4] Verifying loaded data...
📊 Data Verification:
  - Total records: 222
  - Unique symbols: 57
  - Buy/Sell breakdown:
    • BUY: 111
    • SELL: 111
```

## Flask Web Application

### Setup and Run

```bash
cd TMNAS/ETL/python_db
pip install -r requirements.txt
python app.py
```

The application will start on `http://localhost:5000` (configurable via `.env`).

### Features

- 🔍 Browse database tables
- 📝 View and edit records
- 📋 Automatic audit logging
- 🔐 Input validation and SQL injection prevention
- 📊 Real-time data verification
- 🚨 Comprehensive error handling

### Configuration

Edit `.env` to configure:

```env
FLASK_ENV=development      # development or production
DEBUG=False                 # Set to True for development only
FLASK_PORT=5000           # Port to run Flask app
DEFAULT_SCHEMA=bse        # Default database schema
```

### API Endpoints

#### View Tables
```
GET /
```
List all available tables in the schema

#### View Table Data
```
GET /table/<table_name>?limit=100
```
View data from a specific table

#### Update Record
```
POST /api/update_record/<table_name>
Content-Type: application/json

{
  "record_id": "1|2|3",  // Composite key support
  "updates": {
    "column_name": "new_value"
  }
}
```

## Testing

### Run Unit Tests

```bash
cd TMNAS/ETL/python_db
python -m pytest test_database.py -v
```

### Run with Coverage

```bash
python -m pytest test_database.py -v --cov=. --cov-report=html
```

## Environment Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| DB_HOST | localhost | Database host |
| DB_PORT | 5432 | Database port |
| DB_NAME | BSENSE | Database name |
| DB_USER | postgres | Database user |
| DB_PASSWORD | (required) | Database password |
| DEFAULT_SCHEMA | bse | Default schema |
| FLASK_ENV | development | Flask environment |
| DEBUG | False | Debug mode |
| FLASK_PORT | 5000 | Flask port |

## Project Structure

```
ETL_Manish/
├── .env.example              # Example environment configuration
├── .gitignore               # Git ignore rules
├── SECURITY.md              # Security documentation
├── README.md                # This file
└── TMNAS/
    └── ETL/
        ├── requirements.txt           # Python dependencies
        ├── postgres_connector.py      # Database connection module
        ├── create_manager_table.py    # Manager table creation
        ├── load_bulk_data.py          # Bulk CSV loader
        ├── app.py                     # Flask application
        ├── python_db/
        │   ├── requirements.txt       # Flask app dependencies
        │   ├── app.py                 # Main Flask app
        │   ├── test_database.py       # Unit tests
        │   ├── templates/
        │   │   ├── index.html
        │   │   └── table.html
        │   └── Output/
        │       └── *.csv
        └── sql/
            └── create_manager_table.sql
```

## Security Best Practices

✅ **DO:**
- Use environment variables for all credentials
- Validate all user input
- Keep `.env` file in `.gitignore`
- Run tests before deployment
- Monitor audit logs regularly

❌ **DON'T:**
- Hardcode credentials in source code
- Use default passwords in production
- Commit `.env` file to version control
- Skip input validation
- Ignore error logs

For detailed security information, see [SECURITY.md](SECURITY.md).

## Troubleshooting

### Connection Failed
```
Error: Environment variable DB_PASSWORD not found
```
**Solution:** Create `.env` file with valid credentials

### SQL Injection Error
```
Error: Invalid identifier
```
**Solution:** Table/column names must contain only alphanumeric characters and underscores

### Port Already in Use
```
Address already in use
```
**Solution:** Change FLASK_PORT in `.env` or stop other services using that port

## Support

For issues or questions:
1. Check [SECURITY.md](SECURITY.md) for common issues
2. Review log output for error details
3. Run unit tests: `pytest test_database.py -v`
4. Check database credentials in `.env`

## License

[Add your license here]

## Contributors

[Add contributors here]
