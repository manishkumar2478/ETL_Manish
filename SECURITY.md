# Security & Setup Guide

## Environment Configuration

### 1. Create `.env` File
Copy `.env.example` and create a `.env` file with your database credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your actual credentials:

```env
# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=BSENSE
DB_USER=postgres
DB_PASSWORD=your_secure_password_here

# Application Configuration
FLASK_ENV=development
DEBUG=False
FLASK_PORT=5000

# Schema Configuration
DEFAULT_SCHEMA=bse
```

**IMPORTANT:** Never commit `.env` file to version control. It's listed in `.gitignore`.

## Security Fixes Implemented

### ✅ 1. Removed Hardcoded Credentials
- **Before:** Passwords embedded in source code (e.g., `Admin@123`)
- **After:** All credentials loaded from environment variables via `.env` file
- **Files Updated:**
  - `postgres_connector.py`
  - `create_manager_table.py`
  - `app.py`
  - `load_bulk_data.py`

### ✅ 2. Fixed SQL Injection Vulnerability
- **Before:** `f"SELECT * FROM {full_table_name} LIMIT {limit};"`
- **After:** Parameterized queries with input validation
- **Files Updated:**
  - `app.py` - `extract_table_data()` function

**Example Fix:**
```python
# Before (vulnerable)
query = f"SELECT * FROM {full_table_name} LIMIT {limit};"
cursor.execute(query)

# After (safe)
def validate_identifier(identifier):
    """Validate identifier contains only safe characters"""
    import re
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}")
    return identifier

schema_name = validate_identifier(schema_name)
table_name = validate_identifier(table_name)
query = f"SELECT * FROM {schema_name}.{table_name} LIMIT %s;"
cursor.execute(query, (limit,))
```

### ✅ 3. Added Input Validation
- **Added:** `validate_identifier()` function to prevent SQL injection
- **Coverage:** All table names, schema names, and column references
- **Files Updated:**
  - `app.py` - New validation function and applied to all endpoints

### ✅ 4. Improved Error Handling & Logging
- **Added:** Comprehensive logging using Python's `logging` module
- **Features:**
  - Log levels: INFO, WARNING, ERROR
  - Database operation tracking
  - Error context and debugging information
- **Files Updated:**
  - All Python files

**Log Output Example:**
```
2024-01-15 10:30:45 - INFO - Connection to PostgreSQL successful (DB: BSENSE)
2024-01-15 10:30:46 - INFO - ✓ Data loaded successfully!
2024-01-15 10:30:47 - ERROR - Error executing query: duplicate key value violates unique constraint
```

### ✅ 5. Standardized Database Configuration
- **Before:** Different databases and configurations across modules
  - `/ETL/`: Used `etl_db`
  - `/python_db/`: Used `BSENSE`
- **After:** All use environment variables and can be configured consistently
- **Configuration:** Set via `.env` file

### ✅ 6. Enhanced Requirements Management
- **Added:** Flask dependency
- **Added:** Testing dependencies (pytest, pytest-cov)
- **Files:**
  - `requirements.txt` (ETL directory)
  - `python_db/requirements.txt`

**Installation:**
```bash
pip install -r requirements.txt
```

### ✅ 7. Added Unit Tests
- **File:** `python_db/test_database.py`
- **Coverage:**
  - Database connection tests
  - Input validation tests
  - SQL injection prevention tests
  - Error handling tests
  - Audit logging tests
  - Flask endpoint tests

**Running Tests:**
```bash
cd TMNAS/ETL/python_db
pip install -r requirements.txt
python -m pytest test_database.py -v
```

### ✅ 8. Added Authentication Decorator (Foundation)
- **File:** `app.py`
- **Feature:** `@require_auth` decorator for future authentication implementation
- **Usage:** Can be extended to add JWT or session-based authentication

## Database Connection Examples

### Before (Insecure)
```python
conn = create_connection(
    host="localhost",
    port="5432",
    database="BSENSE",
    user="postgres",
    password="Admin@123",  # ❌ HARDCODED!
)
```

### After (Secure)
```python
# Uses environment variables automatically
conn = create_connection()

# Or with override
conn = create_connection(database_name='OTHER_DB')
```

## Best Practices

### ✅ DO
- Use environment variables for all sensitive data
- Validate all user input
- Use parameterized queries
- Log all database operations
- Keep `.env` in `.gitignore`
- Run unit tests regularly

### ❌ DON'T
- Hardcode credentials in source code
- Use string formatting for SQL queries
- Ignore errors silently
- Commit `.env` file to Git
- Use default passwords in production

## Audit Logging

All database updates are automatically logged with:
- Table name
- Record ID
- Operation type (INSERT, UPDATE, DELETE)
- Old data (before update)
- New data (after update)
- User/system that made the change
- Timestamp

**Query audit logs:**
```sql
SELECT * FROM bse.audit_log 
WHERE updated_at > NOW() - INTERVAL '1 hour'
ORDER BY updated_at DESC;
```

## Configuration Management

### Environment Variables
All configurable via `.env`:
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)
- `DB_NAME` - Database name (default: BSENSE)
- `DB_USER` - Database user (default: postgres)
- `DB_PASSWORD` - Database password (required)
- `DEFAULT_SCHEMA` - Default schema (default: bse)
- `DEBUG` - Debug mode (default: False)
- `FLASK_PORT` - Flask port (default: 5000)

## Testing & Validation

### Run All Tests
```bash
python -m pytest test_database.py -v --cov=. --cov-report=html
```

### Test Specific Category
```bash
# Test input validation
python -m pytest test_database.py::TestInputValidation -v

# Test error handling
python -m pytest test_database.py::TestErrorHandling -v
```

## Migration Guide (From Old Code)

### Step 1: Set up Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Update Code References
- Remove any hardcoded `DB_PASSWORD` values
- Replace `create_connection(host=..., port=..., database=..., user=..., password=...)` with `create_connection()`
- All other function signatures remain the same

### Step 4: Run Tests
```bash
python -m pytest test_database.py -v
```

## Troubleshooting

### Connection Issues
```
Error: Environment variable DB_PASSWORD not found
```
**Solution:** Create `.env` file with DB_PASSWORD

```
Error: Invalid identifier
```
**Solution:** Check table/column names contain only alphanumeric and underscore characters

### SQL Injection Prevention
All table and column names are validated. If you get "Invalid identifier" errors:
- Ensure names follow SQL identifier rules
- Use underscores instead of hyphens
- No spaces in identifiers

## Compliance & Security Standards

✅ **OWASP Top 10 - Addressed:**
- A01:2021 - Broken Access Control (Input validation)
- A02:2021 - Cryptographic Failures (Environment variables)
- A03:2021 - Injection (SQL injection prevention)

✅ **CWE Mitigations:**
- CWE-89: SQL Injection → Parameterized queries
- CWE-79: Cross-site Scripting → Input validation
- CWE-798: Use of Hard-coded Credentials → Environment variables

## Support & Documentation

For more information, see:
- [PostgreSQL Connection Documentation](https://www.postgresql.org/docs/current/libpq-connect.html)
- [Python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [Flask Security Best Practices](https://flask.palletsprojects.com/security/)
