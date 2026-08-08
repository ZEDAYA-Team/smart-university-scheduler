from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)  # admin, department_head, lecturer, student
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    role = relationship("Role", back_populates="users")
    lecturer = relationship("Lecturer", back_populates="user", uselist=False)
    student = relationship("Student", back_populates="user", uselist=False)
