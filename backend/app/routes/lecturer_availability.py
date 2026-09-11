"""
Lecturer availability -- when a lecturer is free or unavailable during the
week. What Conflict Detection and the OR-Tools solver check unavailability
against.

This is a custom router rather than the generic CRUD factory
(app/routes/factory.py) on purpose: every operation here is scoped to a
specific lecturer via the URL path (/lecturers/{lecturer_id}/availability),
and lecturer_id deliberately never comes from the request body. Using the
generic factory here would let a client edit or delete another lecturer's
availability row just by guessing its availability_id, since the factory
only checks "does this row exist," not "does this row belong to the
lecturer in the URL." Every read/write below checks both.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.models import Lecturer, LecturerAvailability
from app.schemas.setup import (
    LecturerAvailabilityCreate,
    LecturerAvailabilityUpdate,
    LecturerAvailabilityResponse,
)

router = APIRouter(prefix="/lecturers/{lecturer_id}/availability", tags=["Lecturer Availability"])


def _get_lecturer_or_404(db: Session, lecturer_id: int) -> Lecturer:
    lecturer = db.query(Lecturer).filter(Lecturer.lecturer_id == lecturer_id).first()
    if lecturer is None:
        raise HTTPException(status_code=404, detail="Lecturer not found")
    return lecturer


def _get_scoped_entry_or_404(db: Session, lecturer_id: int, availability_id: int) -> LecturerAvailability:
    """Fetches an availability row ONLY if it belongs to this lecturer --
    the actual fix for the IDOR risk described above."""
    entry = (
        db.query(LecturerAvailability)
        .filter(
            LecturerAvailability.availability_id == availability_id,
            LecturerAvailability.lecturer_id == lecturer_id,
        )
        .first()
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Availability entry not found for this lecturer")
    return entry


@router.get("", response_model=List[LecturerAvailabilityResponse])
def list_availability(lecturer_id: int, db: Session = Depends(get_db)):
    _get_lecturer_or_404(db, lecturer_id)
    return (
        db.query(LecturerAvailability)
        .filter(LecturerAvailability.lecturer_id == lecturer_id)
        .all()
    )


@router.post("", response_model=LecturerAvailabilityResponse, status_code=status.HTTP_201_CREATED)
def add_availability(lecturer_id: int, payload: LecturerAvailabilityCreate, db: Session = Depends(get_db)):
    _get_lecturer_or_404(db, lecturer_id)

    # The DB has CHECK(end_time > start_time) already -- this proactive
    # check just gives a clean 422 instead of a raw SQL error surfacing
    # through the generic except-block below.
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=422, detail="end_time must be after start_time")

    entry = LecturerAvailability(lecturer_id=lecturer_id, **payload.model_dump())
    db.add(entry)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    db.refresh(entry)
    return entry


@router.patch("/{availability_id}", response_model=LecturerAvailabilityResponse)
def update_availability(
    lecturer_id: int,
    availability_id: int,
    payload: LecturerAvailabilityUpdate,
    db: Session = Depends(get_db),
):
    _get_lecturer_or_404(db, lecturer_id)
    entry = _get_scoped_entry_or_404(db, lecturer_id, availability_id)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)

    # Re-check after merging the update, in case only start_time or only
    # end_time was changed -- either alone could produce an invalid range.
    if entry.end_time <= entry.start_time:
        db.rollback()
        raise HTTPException(status_code=422, detail="end_time must be after start_time")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    db.refresh(entry)
    return entry


@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability(lecturer_id: int, availability_id: int, db: Session = Depends(get_db)):
    _get_lecturer_or_404(db, lecturer_id)
    entry = _get_scoped_entry_or_404(db, lecturer_id, availability_id)
    db.delete(entry)
    db.commit()
    return None