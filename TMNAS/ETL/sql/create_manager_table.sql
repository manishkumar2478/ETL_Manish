CREATE SCHEMA IF NOT EXISTS bse;

CREATE TABLE IF NOT EXISTS bse.manager (
    manager_id   SERIAL       PRIMARY KEY,
    manager_name VARCHAR(255) NOT NULL,
    employee_count INTEGER    NOT NULL DEFAULT 0
);
