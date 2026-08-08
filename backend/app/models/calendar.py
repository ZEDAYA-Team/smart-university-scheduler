from sqlalchemy import Column, Integer, String, Time, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class AcademicYear(Base):
    __tablename__ = "academic_years"

    academic_year_id = Column(Integer, primary_key=True)
    label = Column(String(20), nullable=False, unique=True)  # e.g. '2025/2026'

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    semesters = relationship("Semester", back_populates="academic_year")


class Semester(Base):
    __tablename__ = "semesters"

    semester_id = Column(Integer, primary_key=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.academic_year_id"), nullable=False)
    name = Column(String(50), nullable=False)  # e.g. 'Semester 1'

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("academic_year_id", "name", name="uq_semesters_year_name"),)

    academic_year = relationship("AcademicYear", back_populates="semesters")
    course_offerings = relationship("CourseOffering", back_populates="semester")
    timetables = relationship("Timetable", back_populates="semester")


class TimeSlot(Base):
    """Fixed predefined slots (confirmed decision) -- keeps the OR-Tools
    model simple. Not freeform start/end times per section."""

    __tablename__ = "time_slots"

    slot_id = Column(Integer, primary_key=True)
    day = Column(String(10), nullable=False)  # 'Monday', 'Tuesday', ...
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("day", "start_time", "end_time", name="uq_time_slots_day_start_end"),
        CheckConstraint("end_time > start_time", name="ck_time_slots_end_after_start"),
    )

    schedule_entries = relationship("ScheduleEntry", back_populates="time_slot")
