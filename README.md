# ETL_Manish

## TMNAS / ETL

### PostgreSQL Connector

A Python utility for connecting to PostgreSQL databases and executing queries.

#### Setup

```bash
pip install -r TMNAS/ETL/requirements.txt
```

#### Usage

Update the connection parameters in `TMNAS/ETL/postgres_connector.py` with your database credentials, then run:

```bash
python TMNAS/ETL/postgres_connector.py
```

### Manager Table (bse schema)

Creates the `bse.manager` table with the following columns:

| Column         | Type         | Description                          |
|----------------|--------------|--------------------------------------|
| manager_id     | SERIAL (PK)  | Auto-incrementing manager identifier |
| manager_name   | VARCHAR(255) | Name of the manager                  |
| employee_count | INTEGER      | Number of employees under the manager|

#### Usage

Update the connection parameters in `TMNAS/ETL/create_manager_table.py`, then run:

```bash
python TMNAS/ETL/create_manager_table.py
```

Alternatively, execute the raw SQL directly:

```bash
psql -h localhost -U your_username -d your_database -f TMNAS/ETL/sql/create_manager_table.sql
```
