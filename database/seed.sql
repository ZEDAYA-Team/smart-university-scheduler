-- Demo data only: CNCS pilot reporting dashboard.
INSERT INTO semesters (id, name, academic_year, starts_on, ends_on) VALUES
  (1, 'Semester I', '2026/27', '2026-09-14', '2027-01-29') ON CONFLICT (id) DO NOTHING;
INSERT INTO departments (id, name, code) VALUES
  (1, 'Computer Science', 'CS'), (2, 'Mathematics', 'MATH'), (3, 'Physics', 'PHYS') ON CONFLICT (id) DO NOTHING;
INSERT INTO lecturers (id, full_name, department_id, max_teaching_hours) VALUES
  (1, 'Dr. Meron Assefa', 1, 18), (2, 'Dr. Solomon Tadesse', 2, 16), (3, 'Ms. Selamawit Worku', 3, 14) ON CONFLICT (id) DO NOTHING;
INSERT INTO rooms (id, code, name, capacity, available_hours) VALUES
  (1, 'CNCS-201', 'CNCS Building Room 201', 80, 22), (2, 'CNCS-104', 'CNCS Building Room 104', 60, 20), (3, 'LAB-3', 'Computer Lab 3', 35, 18), (4, 'CNCS-305', 'CNCS Building Room 305', 55, 20) ON CONFLICT (id) DO NOTHING;
INSERT INTO schedule_entries (semester_id, department_id, lecturer_id, room_id, course_code, course_title, session_date, starts_at, ends_at) VALUES
  (1, 1, 1, 1, 'CS301', 'Database Systems', '2026-09-15', '08:00', '10:00'),
  (1, 1, 1, 1, 'CS303', 'Operating Systems', '2026-09-17', '08:00', '10:00'),
  (1, 2, 2, 2, 'MATH201', 'Linear Algebra', '2026-09-15', '10:00', '13:00'),
  (1, 2, 2, 4, 'MATH204', 'Numerical Methods', '2026-09-17', '10:00', '13:00'),
  (1, 3, 3, 3, 'PHYS210', 'Electromagnetism Lab', '2026-09-16', '13:00', '16:00'),
  (1, 1, 1, 3, 'CS310', 'Software Engineering', '2026-09-18', '13:00', '17:00') ON CONFLICT DO NOTHING;
INSERT INTO conflict_events (semester_id, conflict_type, description, severity, status) VALUES
  (1, 'room_overlap', 'CNCS-201 · Tuesday 10:00', 'critical', 'open'),
  (1, 'capacity', 'STAT-2A · Lab-1', 'critical', 'open'),
  (1, 'lecturer_availability', 'Dr. M. Assefa · Monday 14:00', 'warning', 'review') ON CONFLICT DO NOTHING;
