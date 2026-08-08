"""
Import every model here so Base.metadata is fully populated -- this is
what Alembic's autogenerate reads, and what create_all() uses in tests.

Adding a new model? Add its import below or Alembic won't see it.
"""

from app.models.auth import Role, User
from app.models.academic import Faculty, Department, Program, Course, Section
from app.models.people import Lecturer, Student, LecturerAvailability
from app.models.resources import Building, Room
from app.models.calendar import AcademicYear, Semester, TimeSlot
from app.models.scheduling import (
    CourseOffering,
    Timetable,
    ScheduleEntry,
    ScheduleRequest,
    Enrollment,
)

__all__ = [
    "Role",
    "User",
    "Faculty",
    "Department",
    "Program",
    "Course",
    "Section",
    "Lecturer",
    "Student",
    "LecturerAvailability",
    "Building",
    "Room",
    "AcademicYear",
    "Semester",
    "TimeSlot",
    "CourseOffering",
    "Timetable",
    "ScheduleEntry",
    "ScheduleRequest",
    "Enrollment",
]
