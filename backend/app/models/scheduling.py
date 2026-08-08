from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class CourseOffering(Base):
    """A specific course, taught by a specific lecturer, to a specific
    section, in a specific semester. This is the thing that actually
    gets scheduled."""

    __tablename__ = "course_offerings"

    offering_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.semester_id"), nullable=False)
    lecturer_id = Column(Integer, ForeignKey("lecturers.lecturer_id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.section_id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("course_id", "semester_id", "section_id", name="uq_offerings_course_semester_section"),
    )

    course = relationship("Course", back_populates="offerings")
    semester = relationship("Semester", back_populates="course_offerings")
    lecturer = relationship("Lecturer", back_populates="offerings")
    section = relationship("Section", back_populates="offerings")
    schedule_entries = relationship("ScheduleEntry", back_populates="offering")
    enrollments = relationship("Enrollment", back_populates="offering")


class Timetable(Base):
    """A version of a semester's schedule: draft, published, or archived."""

    __tablename__ = "timetables"

    timetable_id = Column(Integer, primary_key=True)
    semester_id = Column(Integer, ForeignKey("semesters.semester_id"), nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published', 'archived')", name="ck_timetables_status_valid"),
    )

    semester = relationship("Semester", back_populates="timetables")
    schedule_entries = relationship("ScheduleEntry", back_populates="timetable")


class ScheduleEntry(Base):
    """The heart of the schema: places one course offering into one room
    and one time slot, within one timetable version. Conflict detection
    scans this table for overlaps.

    DB-level enforcement note: the UniqueConstraint below stops a room from
    being double-booked in the same timetable/slot. Lecturer- and
    student-level conflicts can't be expressed as a simple column-level
    constraint here, since lecturer/student are reached via course_offering,
    not stored directly on this table -- those checks belong to the
    Conflict Detection module and the OR-Tools solver, by design.
    """

    __tablename__ = "schedule_entries"

    entry_id = Column(Integer, primary_key=True)
    timetable_id = Column(Integer, ForeignKey("timetables.timetable_id"), nullable=False)
    offering_id = Column(Integer, ForeignKey("course_offerings.offering_id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("time_slots.slot_id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("timetable_id", "room_id", "slot_id", name="uq_schedule_entries_timetable_room_slot"),
    )

    timetable = relationship("Timetable", back_populates="schedule_entries")
    offering = relationship("CourseOffering", back_populates="schedule_entries")
    room = relationship("Room", back_populates="schedule_entries")
    time_slot = relationship("TimeSlot", back_populates="schedule_entries")
    requests = relationship("ScheduleRequest", back_populates="entry")


class ScheduleRequest(Base):
    """A request to change a schedule entry -- gives manual edits an
    audit trail."""

    __tablename__ = "schedule_requests"

    request_id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey("schedule_entries.entry_id"), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    reason = Column(Text)
    status = Column(String(20), nullable=False, default="pending")

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="ck_schedule_requests_status_valid"),
    )

    entry = relationship("ScheduleEntry", back_populates="requests")


class Enrollment(Base):
    """Links a student to a course offering (not just a course) -- this is
    what makes student-level conflict detection possible."""

    __tablename__ = "enrollments"

    enrollment_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    offering_id = Column(Integer, ForeignKey("course_offerings.offering_id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("student_id", "offering_id", name="uq_enrollments_student_offering"),)

    student = relationship("Student", back_populates="enrollments")
    offering = relationship("CourseOffering", back_populates="enrollments")
