-- SQL Schema for Milestone 3 PTO System
-- Run this in your RDS database to manually create tables if init_db() fails

-- Create Requests table
CREATE TABLE IF NOT EXISTS "UKG"."Requests" (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending',
    FOREIGN KEY (employee_id) REFERENCES "UKG"."Employee"("Employee_ID")
);

-- Create Backup_Storage table
CREATE TABLE IF NOT EXISTS "UKG"."Backup_Storage" (
    id SERIAL PRIMARY KEY,
    backup_type VARCHAR(50),
    backup_data JSON,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_pto_employee_id ON "UKG"."Requests"(employee_id);
CREATE INDEX IF NOT EXISTS idx_pto_created_at ON "UKG"."Requests"(created_at);
CREATE INDEX IF NOT EXISTS idx_backups_type ON "UKG"."Backup_Storage"(backup_type);

-- Query to view all PTO requests for an employee
-- Replace 1001 with desired Employee_ID
SELECT 
    id,
    start_date,
    end_date,
    reason,
    status,
    created_at
FROM "UKG"."Requests"
WHERE employee_id = 1001;
ORDER BY created_at DESC;

-- Query to view all active PTO requests
SELECT 
    pr.id,
    pr.employee_id,
    e."First_Name",
    e."Last_Name",
    pr.start_date,
    pr.end_date,
    pr.reason,
    pr.status,
    pr.created_at
FROM "UKG"."Requests" pr
JOIN "UKG"."Employee" e ON pr.employee_id = e."Employee_ID"
WHERE pr.status IN ('pending', 'approved')
ORDER BY pr.start_date ASC;

-- Query to view schedule backups
SELECT 
    id,
    backup_type,
    created_at,
    backup_data
FROM "UKG"."Backup_Storage"
WHERE backup_type = 'schedule'
ORDER BY created_at DESC
LIMIT 10;

-- Query to check if tables exist
SELECT 
    table_name
FROM 
    information_schema.tables
WHERE 
    table_schema = 'UKG' 
    AND table_name IN ('PTO_Requests', 'Backups');

-- Query to view table structure
\d "UKG"."Requests"
\d "UKG"."Backup_Storage"
