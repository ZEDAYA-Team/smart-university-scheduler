from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Faculty(Base):
    __tablename__ = "faculties"

    faculty_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    code = Column(String(20), nullable=False, unique=True)  # e.g. 'CNCS'
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    departments = relationship("Department", back_populates="faculty")


class Department(Base):
    __tablename__ = "departments"

    department_id = Column(Integer, primary_key=True)
    faculty_id = Column(Integer, ForeignKey("faculties.faculty_id"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(20), nullable=False, unique=True)  # e.g. 'CS', 'MATH'
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    faculty = relationship("Faculty", back_populates="departments")
    programs = relationship("Program", back_populates="department")
    courses = relationship("Course", back_populates="department")
    lecturers = relationship("Lecturer", back_populates="department")


class Program(Base):
    __tablename__ = "programs"

    program_id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=False)
    name = Column(String(255), nullable=False)
    level = Column(String(50), nullable=False)  # 'undergraduate', 'masters', ...
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    department = relationship("Department", back_populates="programs")
    sections = relationship("Section", back_populates="program")
    students = relationship("Student", back_populates="program")


class Course(Base):
    """Belongs to a department, not a program directly, so multiple programs
    can share the same course pool instead of duplicating courses."""

    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=False)
    course_code = Column(String(20), nullable=False, unique=True)  # e.g. 'CoSc3071'
    title = Column(String(255), nullable=False)
    credit_hour = Column(Integer, nullable=False)
    course_type = Column(String(50), nullable=False, default="lecture")  # lecture, lab, seminar

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (CheckConstraint("credit_hour > 0", name="ck_courses_credit_hour_positive"),)

    department = relationship("Department", back_populates="courses")
    offerings = relationship("CourseOffering", back_populates="course")


class Section(Base):
    """A cohort of students within a program (e.g. 'CS-3A')."""

    __tablename__ = "sections"

    section_id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey("programs.program_id"), nullable=False)
    name = Column(String(50), nullable=False)  # e.g. 'CS-3A'
    capacity = Column(Integer, nullable=False)  # stored maximum, not a live headcount

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_sections_capacity_positive"),
        UniqueConstraint("program_id", "name", name="uq_sections_program_name"),
    )

    program = relationship("Program", back_populates="sections")
    students = relationship("Student", back_populates="section")
    offerings = relationship("CourseOffering", back_populates="section")
