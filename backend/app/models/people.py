from sqlalchemy import Column, Integer, String, Boolean, Time, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Lecturer(Base):
    __tablename__ = "lecturers"

    lecturer_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=False)
    max_load = Column(Integer, nullable=False, default=12)  # max teaching hours/credits per semester

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="lecturer")
    department = relationship("Department", back_populates="lecturers")
    availability = relationship("LecturerAvailability", back_populates="lecturer")
    offerings = relationship("CourseOffering", back_populates="lecturer")


class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    program_id = Column(Integer, ForeignKey("programs.program_id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.section_id"), nullable=False)
    year_level = Column(Integer, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (CheckConstraint("year_level BETWEEN 1 AND 6", name="ck_students_year_level_range"),)

    user = relationship("User", back_populates="student")
    program = relationship("Program", back_populates="students")
    section = relationship("Section", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student")


class LecturerAvailability(Base):
    """A lecturer's available time windows -- what Conflict Detection checks
    unavailability against."""

    __tablename__ = "lecturer_availability"

    availability_id = Column(Integer, primary_key=True)
    lecturer_id = Column(Integer, ForeignKey("lecturers.lecturer_id"), nullable=False)
    day = Column(String(10), nullable=False)  # 'Monday', 'Tuesday', ...
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    available = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (CheckConstraint("end_time > start_time", name="ck_availability_end_after_start"),)

    lecturer = relationship("Lecturer", back_populates="availability")
