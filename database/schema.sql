-- SUTMS database schema (v1 draft)
-- Fill in as Module 1-3 land. Keep this in sync with backend/app/models/.

-- Example starter table -- replace/expand once the real ER diagram is finalized.
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- admin, dept_head, lecturer, student
    department_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
