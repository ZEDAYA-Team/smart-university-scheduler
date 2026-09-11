# backend/app/routes/__init__.py
from fastapi import APIRouter
from app.routes.factory import create_crud_route
from app.models import (
    Faculty, Department, Building, Room, Lecturer, Program,
    Course, Section, AcademicYear, Semester, TimeSlot
)
from app.schemas import setup as s

# Import custom sub-routers
from app.routes.lecturer_availability import router as lecturer_availability_router
from app.routes.offerings import offerings_router
from app.routes.conflicts import router as conflicts_router  # <--- ADD THIS

setup_router = APIRouter()

configs = [
    (Faculty, s.FacultyCreate, s.FacultyUpdate, s.FacultyResponse, "/faculties", ["Faculties"], "faculty_id"),
    (Department, s.DepartmentCreate, s.DepartmentUpdate, s.DepartmentResponse, "/departments", ["Departments"], "department_id"),
    (Building, s.BuildingCreate, s.BuildingUpdate, s.BuildingResponse, "/buildings", ["Buildings"], "building_id"),
    (Room, s.RoomCreate, s.RoomUpdate, s.RoomResponse, "/rooms", ["Rooms"], "room_id"),
    (Lecturer, s.LecturerCreate, s.LecturerUpdate, s.LecturerResponse, "/lecturers", ["Lecturers"], "lecturer_id"),
    (Program, s.ProgramCreate, s.ProgramUpdate, s.ProgramResponse, "/programs", ["Programs"], "program_id"),
    (Course, s.CourseCreate, s.CourseUpdate, s.CourseResponse, "/courses", ["Courses"], "course_id"),
    (Section, s.SectionCreate, s.SectionUpdate, s.SectionResponse, "/sections", ["Sections"], "section_id"),
    (AcademicYear, s.AcademicYearCreate, s.AcademicYearUpdate, s.AcademicYearResponse, "/academic-years", ["Academic Years"], "academic_year_id"),
    (Semester, s.SemesterCreate, s.SemesterUpdate, s.SemesterResponse, "/semesters", ["Semesters"], "semester_id"),
    (TimeSlot, s.TimeSlotCreate, s.TimeSlotUpdate, s.TimeSlotResponse, "/time-slots", ["Time Slots"], "slot_id"),
]

for model, c_schema, u_schema, r_schema, prefix, tags, id_field in configs:
    sub_router = create_crud_route(model, c_schema, u_schema, r_schema, prefix, tags, id_field)
    setup_router.include_router(sub_router)

__all__ = [
    "setup_router",
    "offerings_router",
    "lecturer_availability_router",
    "conflicts_router",  # <--- ADD THIS
]