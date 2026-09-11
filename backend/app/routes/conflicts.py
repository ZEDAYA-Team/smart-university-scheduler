from datetime import time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.services.conflict_detector import ConflictDetector

router = APIRouter(prefix="/conflicts", tags=["Conflict Detection"])

@router.get("/validate-assignment")
def validate_assignment(
    lecturer_id: int,
    room_id: int,
    section_id: int,
    day: str,
    start_time: time,
    end_time: time,
    db: Session = Depends(get_db)
):
    detector = ConflictDetector(db)
    conflicts = []

    # 1. Check Capacity
    cap_check = detector.check_room_capacity(room_id, section_id)
    if cap_check["has_conflict"]:
        conflicts.append(cap_check)

    # 2. Check Availability
    avail_check = detector.check_lecturer_unavailability(lecturer_id, day, start_time, end_time)
    if avail_check["has_conflict"]:
        conflicts.append(avail_check)

    return {
        "valid": len(conflicts) == 0,
        "conflict_count": len(conflicts),
        "conflicts": conflicts
    }