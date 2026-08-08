-- SUTMS database schema
-- Matches docs/database/SUTMS_ERD_Design.docx — the ERD is the source of truth,
-- =========================================================
-- Roles & Users
-- =========================================================

CREATE TABLE roles (
    role_id     SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE, -- admin, department_head, lecturer, student
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    user_id        SERIAL PRIMARY KEY,
    first_name     VARCHAR(100) NOT NULL,
    last_name      VARCHAR(100) NOT NULL,
    email          VARCHAR(255) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,
    role_id        INTEGER NOT NULL REFERENCES roles(role_id),
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_role_id ON users(role_id);

-- =========================================================
-- Organizational hierarchy: Faculty -> Department -> Program / Course
-- =========================================================

CREATE TABLE faculties (
    faculty_id  SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    code        VARCHAR(20) NOT NULL UNIQUE, -- e.g. 'CNCS'
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE departments (
    department_id  SERIAL PRIMARY KEY,
    faculty_id     INTEGER NOT NULL REFERENCES faculties(faculty_id),
    name           VARCHAR(255) NOT NULL,
    code           VARCHAR(20) NOT NULL UNIQUE, -- e.g. 'CS', 'MATH'
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_departments_faculty_id ON departments(faculty_id);

CREATE TABLE programs (
    program_id     SERIAL PRIMARY KEY,
    department_id  INTEGER NOT NULL REFERENCES departments(department_id),
    name           VARCHAR(255) NOT NULL,
    level          VARCHAR(50) NOT NULL, -- e.g. 'undergraduate', 'masters'
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_programs_department_id ON programs(department_id);

-- Courses belong to a department, not a program directly, so multiple
-- programs can share the same course pool instead of duplicating courses.
CREATE TABLE courses (
    course_id      SERIAL PRIMARY KEY,
    department_id  INTEGER NOT NULL REFERENCES departments(department_id),
    course_code    VARCHAR(20) NOT NULL UNIQUE, -- e.g. 'CoSc3071'
    title          VARCHAR(255) NOT NULL,
    credit_hour    INTEGER NOT NULL CHECK (credit_hour > 0),
    course_type    VARCHAR(50) NOT NULL DEFAULT 'lecture', -- lecture, lab, seminar, etc.
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_courses_department_id ON courses(department_id);

-- A section is a cohort of students within a program (e.g. "CS-3A").
CREATE TABLE sections (
    section_id  SERIAL PRIMARY KEY,
    program_id  INTEGER NOT NULL REFERENCES programs(program_id),
    name        VARCHAR(50) NOT NULL, -- e.g. 'CS-3A'
    capacity    INTEGER NOT NULL CHECK (capacity > 0), -- stored maximum, not a live headcount
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (program_id, name)
);

CREATE INDEX idx_sections_program_id ON sections(program_id);

-- =========================================================
-- People: Lecturer / Student extend User
-- =========================================================

CREATE TABLE lecturers (
    lecturer_id    SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL UNIQUE REFERENCES users(user_id),
    department_id  INTEGER NOT NULL REFERENCES departments(department_id),
    max_load       INTEGER NOT NULL DEFAULT 12, -- max teaching hours/credits per semester
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_lecturers_department_id ON lecturers(department_id);

CREATE TABLE students (
    student_id  SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL UNIQUE REFERENCES users(user_id),
    program_id  INTEGER NOT NULL REFERENCES programs(program_id),
    section_id  INTEGER NOT NULL REFERENCES sections(section_id),
    year_level  INTEGER NOT NULL CHECK (year_level BETWEEN 1 AND 6),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_students_program_id ON students(program_id);
CREATE INDEX idx_students_section_id ON students(section_id);

-- A lecturer's available time windows -- what Conflict Detection checks
-- unavailability against.
CREATE TABLE lecturer_availability (
    availability_id  SERIAL PRIMARY KEY,
    lecturer_id      INTEGER NOT NULL REFERENCES lecturers(lecturer_id),
    day              VARCHAR(10) NOT NULL, -- 'Monday', 'Tuesday', ...
    start_time       TIME NOT NULL,
    end_time         TIME NOT NULL,
    available        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    CHECK (end_time > start_time)
);

CREATE INDEX idx_availability_lecturer_id ON lecturer_availability(lecturer_id);

-- =========================================================
-- Physical resources (single campus -- no CAMPUS table)
-- =========================================================

CREATE TABLE buildings (
    building_id  SERIAL PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE rooms (
    room_id      SERIAL PRIMARY KEY,
    building_id  INTEGER NOT NULL REFERENCES buildings(building_id),
    room_number  VARCHAR(20) NOT NULL,
    capacity     INTEGER NOT NULL CHECK (capacity > 0),
    room_type    VARCHAR(50) NOT NULL DEFAULT 'lecture', -- lecture, lab
    created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (building_id, room_number)
);

CREATE INDEX idx_rooms_building_id ON rooms(building_id);

-- =========================================================
-- Time structure
-- =========================================================

CREATE TABLE academic_years (
    academic_year_id  SERIAL PRIMARY KEY,
    label              VARCHAR(20) NOT NULL UNIQUE, -- e.g. '2025/2026'
    created_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE semesters (
    semester_id       SERIAL PRIMARY KEY,
    academic_year_id  INTEGER NOT NULL REFERENCES academic_years(academic_year_id),
    name              VARCHAR(50) NOT NULL, -- e.g. 'Semester 1'
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (academic_year_id, name)
);

CREATE INDEX idx_semesters_academic_year_id ON semesters(academic_year_id);

-- Fixed predefined slots (confirmed decision) -- keeps the OR-Tools model simple.
CREATE TABLE time_slots (
    slot_id     SERIAL PRIMARY KEY,
    day         VARCHAR(10) NOT NULL, -- 'Monday', 'Tuesday', ...
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (day, start_time, end_time),
    CHECK (end_time > start_time)
);

-- =========================================================
-- Scheduling core
-- =========================================================

-- A specific course, taught by a specific lecturer, to a specific section,
-- in a specific semester. This is the thing that actually gets scheduled.
CREATE TABLE course_offerings (
    offering_id  SERIAL PRIMARY KEY,
    course_id    INTEGER NOT NULL REFERENCES courses(course_id),
    semester_id  INTEGER NOT NULL REFERENCES semesters(semester_id),
    lecturer_id  INTEGER NOT NULL REFERENCES lecturers(lecturer_id),
    section_id   INTEGER NOT NULL REFERENCES sections(section_id),
    created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (course_id, semester_id, section_id) -- no duplicate offering of the same course to the same section in the same semester
);

CREATE INDEX idx_offerings_semester_id ON course_offerings(semester_id);
CREATE INDEX idx_offerings_lecturer_id ON course_offerings(lecturer_id);
CREATE INDEX idx_offerings_section_id ON course_offerings(section_id);

-- A version of a semester's schedule: draft, published, or archived.
CREATE TABLE timetables (
    timetable_id  SERIAL PRIMARY KEY,
    semester_id   INTEGER NOT NULL REFERENCES semesters(semester_id),
    status        VARCHAR(20) NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft', 'published', 'archived')),
    created_by    INTEGER NOT NULL REFERENCES users(user_id),
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_timetables_semester_id ON timetables(semester_id);

-- The heart of the schema: places one course offering into one room and one
-- time slot, within one timetable version. Conflict detection scans this
-- table for overlaps.
--
-- DB-level enforcement note: the UNIQUE constraint below stops a room from
-- being double-booked in the same timetable/slot. Lecturer- and
-- student-level conflicts (a lecturer or student double-booked) can't be
-- expressed as a simple column-level UNIQUE here, since lecturer/student
-- are reached via course_offering, not stored directly on this table. Those
-- checks are enforced by the Conflict Detection module (Module 5) and the
-- OR-Tools solver, not the database -- that's the intended design.
CREATE TABLE schedule_entries (
    entry_id      SERIAL PRIMARY KEY,
    timetable_id  INTEGER NOT NULL REFERENCES timetables(timetable_id),
    offering_id   INTEGER NOT NULL REFERENCES course_offerings(offering_id),
    room_id       INTEGER NOT NULL REFERENCES rooms(room_id),
    slot_id       INTEGER NOT NULL REFERENCES time_slots(slot_id),
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (timetable_id, room_id, slot_id) -- prevents room double-booking within a timetable
);

CREATE INDEX idx_schedule_entries_timetable_id ON schedule_entries(timetable_id);
CREATE INDEX idx_schedule_entries_offering_id ON schedule_entries(offering_id);
CREATE INDEX idx_schedule_entries_room_id ON schedule_entries(room_id);
CREATE INDEX idx_schedule_entries_slot_id ON schedule_entries(slot_id);

-- A request to change a schedule entry -- gives manual edits an audit trail.
CREATE TABLE schedule_requests (
    request_id    SERIAL PRIMARY KEY,
    entry_id      INTEGER NOT NULL REFERENCES schedule_entries(entry_id),
    requested_by  INTEGER NOT NULL REFERENCES users(user_id),
    reason        TEXT,
    status        VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_schedule_requests_entry_id ON schedule_requests(entry_id);

-- Links a student to a course offering (not just a course) -- this is what
-- makes student-level conflict detection possible.
CREATE TABLE enrollments (
    enrollment_id  SERIAL PRIMARY KEY,
    student_id     INTEGER NOT NULL REFERENCES students(student_id),
    offering_id    INTEGER NOT NULL REFERENCES course_offerings(offering_id),
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, offering_id) -- prevents duplicate enrollment
);

CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_offering_id ON enrollments(offering_id);