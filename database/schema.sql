-- SUTMS dashboard and reporting support schema.
-- Core scheduling modules may add their own tables later; these are the
-- minimum reporting-side entities and read-only views used by this module.

CREATE TABLE IF NOT EXISTS semesters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    starts_on DATE NOT NULL,
    ends_on DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    code VARCHAR(15) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS lecturers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    max_teaching_hours NUMERIC(6, 2) NOT NULL CHECK (max_teaching_hours > 0)
);

CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    available_hours NUMERIC(6, 2) NOT NULL DEFAULT 40 CHECK (available_hours > 0)
);

CREATE TABLE IF NOT EXISTS schedule_entries (
    id SERIAL PRIMARY KEY,
    semester_id INTEGER NOT NULL REFERENCES semesters(id),
    department_id INTEGER NOT NULL REFERENCES departments(id),
    lecturer_id INTEGER NOT NULL REFERENCES lecturers(id),
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    course_code VARCHAR(25) NOT NULL,
    course_title VARCHAR(180) NOT NULL,
    session_date DATE NOT NULL,
    starts_at TIME NOT NULL,
    ends_at TIME NOT NULL,
    CHECK (ends_at > starts_at)
);

CREATE TABLE IF NOT EXISTS conflict_events (
    id SERIAL PRIMARY KEY,
    semester_id INTEGER NOT NULL REFERENCES semesters(id),
    conflict_type VARCHAR(40) NOT NULL CHECK (conflict_type IN ('room_overlap', 'capacity', 'lecturer_availability', 'student_overlap')),
    description TEXT NOT NULL,
    severity VARCHAR(12) NOT NULL CHECK (severity IN ('critical', 'warning', 'info')),
    status VARCHAR(12) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'review', 'resolved')),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_schedule_entries_semester ON schedule_entries(semester_id);
CREATE INDEX IF NOT EXISTS idx_conflict_events_semester ON conflict_events(semester_id, status);

CREATE OR REPLACE VIEW room_utilization_report AS
SELECT
    s.semester_id,
    r.code AS room_code,
    r.name AS room_name,
    COALESCE(SUM(EXTRACT(EPOCH FROM (se.ends_at - se.starts_at)) / 3600), 0)::NUMERIC(8, 2) AS scheduled_hours,
    r.available_hours,
    ROUND(COALESCE(SUM(EXTRACT(EPOCH FROM (se.ends_at - se.starts_at)) / 3600), 0) / r.available_hours * 100, 1) AS utilization_percent
FROM (SELECT DISTINCT semester_id FROM schedule_entries) s
CROSS JOIN rooms r
LEFT JOIN schedule_entries se ON se.semester_id = s.semester_id AND se.room_id = r.id
GROUP BY s.semester_id, r.id;

CREATE OR REPLACE VIEW lecturer_workload_report AS
SELECT
    s.semester_id,
    l.full_name AS lecturer_name,
    d.name AS department_name,
    COALESCE(SUM(EXTRACT(EPOCH FROM (se.ends_at - se.starts_at)) / 3600), 0)::NUMERIC(8, 2) AS assigned_hours,
    l.max_teaching_hours,
    ROUND(COALESCE(SUM(EXTRACT(EPOCH FROM (se.ends_at - se.starts_at)) / 3600), 0) / l.max_teaching_hours * 100, 1) AS load_percent,
    CASE WHEN COALESCE(SUM(EXTRACT(EPOCH FROM (se.ends_at - se.starts_at)) / 3600), 0) / l.max_teaching_hours >= .90 THEN 'near_limit' ELSE 'on_track' END AS status
FROM (SELECT DISTINCT semester_id FROM schedule_entries) s
CROSS JOIN lecturers l
JOIN departments d ON d.id = l.department_id
LEFT JOIN schedule_entries se ON se.semester_id = s.semester_id AND se.lecturer_id = l.id
GROUP BY s.semester_id, l.id, d.name;

CREATE OR REPLACE VIEW department_session_report AS
WITH counts AS (
    SELECT semester_id, department_id, COUNT(*) AS scheduled_sessions
    FROM schedule_entries GROUP BY semester_id, department_id
)
SELECT c.semester_id, d.name AS department_name, c.scheduled_sessions,
       ROUND(c.scheduled_sessions::NUMERIC / SUM(c.scheduled_sessions) OVER (PARTITION BY c.semester_id) * 100, 1) AS session_share_percent
FROM counts c JOIN departments d ON d.id = c.department_id;

CREATE OR REPLACE VIEW conflict_report AS
SELECT semester_id, conflict_type, description, severity, status, detected_at
FROM conflict_events WHERE status <> 'resolved';

CREATE OR REPLACE VIEW dashboard_summary AS
SELECT
    s.id AS semester_id,
    (SELECT COUNT(*) FROM schedule_entries se WHERE se.semester_id = s.id) AS scheduled_sessions,
    (SELECT ROUND(AVG(rur.utilization_percent), 1) FROM room_utilization_report rur WHERE rur.semester_id = s.id) AS average_room_utilization,
    (SELECT COUNT(DISTINCT se.lecturer_id) FROM schedule_entries se WHERE se.semester_id = s.id) AS lecturers_on_schedule,
    (SELECT COUNT(*) FROM conflict_events ce WHERE ce.semester_id = s.id AND ce.status IN ('open', 'review')) AS open_conflicts
FROM semesters s;
