from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Building(Base):
    """Top-level physical resource. AAU CNCS is confirmed single-campus,
    so there's no Campus model above this."""

    __tablename__ = "buildings"

    building_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    rooms = relationship("Room", back_populates="building")


class Room(Base):
    __tablename__ = "rooms"

    room_id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey("buildings.building_id"), nullable=False)
    room_number = Column(String(20), nullable=False)
    capacity = Column(Integer, nullable=False)
    room_type = Column(String(50), nullable=False, default="lecture")  # lecture, lab

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_rooms_capacity_positive"),
        UniqueConstraint("building_id", "room_number", name="uq_rooms_building_room_number"),
    )

    building = relationship("Building", back_populates="rooms")
    schedule_entries = relationship("ScheduleEntry", back_populates="room")
