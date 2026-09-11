"""
Course offerings -- what actually needs to be scheduled for a term.

Reuses the same generic CRUD factory as app/routes/__init__.py's setup
entities, since this is a flat resource (all foreign keys arrive in the
request body, no parent-scoping needed). Mounted separately from
setup_router, though -- offerings is scheduling *input*, not reference
data like faculties/rooms/time-slots, so it deliberately doesn't live
under /api/setup.
"""

from app.routes.factory import create_crud_route
from app.models import CourseOffering
from app.schemas import setup as s

offerings_router = create_crud_route(
    CourseOffering,
    s.CourseOfferingCreate,
    s.CourseOfferingUpdate,
    s.CourseOfferingResponse,
    prefix="/offerings",
    tags=["Course Offerings"],
    id_field="offering_id",
)