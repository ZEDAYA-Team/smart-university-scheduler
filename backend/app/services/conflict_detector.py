"""
Conflict Detection (Module 5).

Checks used by /api/conflicts/validate-assignment before a schedule entry
is created or edited. Each check returns a small self-describing dict
rather than raising -- the route collects all of them and decides what
counts as blocking.

Currently covers:
  - Room capacity vs section size
  - Lecturer unavailability (explicit LecturerAvailability blocks)

Not yet covered here (still open, see review notes):
  - Room double-booking against existing ScheduleEntry rows in a timetable
  - Lecturer double-booking against existing ScheduleEntry rows
  - Student/section overlap via Enrollment
These need a timetable_id (or at least "which other entries count") to be
meaningful, which the current endpoint signature doesn't take yet.
"""

from datetime import time

from sqlalchemy.orm import Session

from app.models import LecturerAvailability, Room, Section


class ConflictDetector:
    def __init__(self, db: Session):
        self.db = db

    def check_room_capacity(self, room_id: int, section_id: int) -> dict:
        room = self.db.query(Room).filter(Room.room_id == room_id).first()
        section = self.db.query(Section).filter(Section.section_id == section_id).first()

        if room is None or section is None:
            return {
                "type": "room_capacity",
                "has_conflict": False,
                "message": "Room or section not found -- capacity check skipped",
            }

        has_conflict = section.capacity > room.capacity
        return {
            "type": "room_capacity",
            "has_conflict": has_conflict,
            "message": (
                f"Section capacity ({section.capacity}) exceeds room capacity ({room.capacity})"
                if has_conflict
                else "Room capacity is sufficient for this section"
            ),
            "room_capacity": room.capacity,
            "section_capacity": section.capacity,
        }

    def check_lecturer_unavailability(
        self, lecturer_id: int, day: str, start_time: time, end_time: time
    ) -> dict:
        blocked_windows = (
            self.db.query(LecturerAvailability)
            .filter(
                LecturerAvailability.lecturer_id == lecturer_id,
                LecturerAvailability.day == day,
                LecturerAvailability.available.is_(False),
            )
            .all()
        )

        overlapping = [
            w for w in blocked_windows if w.start_time < end_time and start_time < w.end_time
        ]
        has_conflict = len(overlapping) > 0

        return {
            "type": "lecturer_availability",
            "has_conflict": has_conflict,
            "message": (
                f"Lecturer is marked unavailable on {day} during part of "
                f"{start_time}-{end_time}"
                if has_conflict
                else "Lecturer has no declared unavailability during this time"
            ),
        }