#schemas/setup.py
from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, Field

# --- FACULTIES ---
class FacultyBase(BaseModel):
    name: str
    code: str

class FacultyCreate(FacultyBase):
    pass

class FacultyUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None

class FacultyResponse(FacultyBase):
    faculty_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- DEPARTMENTS ---
class DepartmentBase(BaseModel):
    faculty_id: int
    name: str
    code: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    faculty_id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None

class DepartmentResponse(DepartmentBase):
    department_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- BUILDINGS ---
class BuildingBase(BaseModel):
    name: str

class BuildingCreate(BuildingBase):
    pass

class BuildingUpdate(BaseModel):
    name: Optional[str] = None

class BuildingResponse(BuildingBase):
    building_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- ROOMS ---
class RoomBase(BaseModel):
    building_id: int
    room_number: str
    capacity: int = Field(..., gt=0)
    room_type: str = "lecture"

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    building_id: Optional[int] = None
    room_number: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    room_type: Optional[str] = None

class RoomResponse(RoomBase):
    room_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- LECTURERS ---
class LecturerBase(BaseModel):
    user_id: int
    department_id: int
    max_load: int = 12

class LecturerCreate(LecturerBase):
    pass

class LecturerUpdate(BaseModel):
    user_id: Optional[int] = None
    department_id: Optional[int] = None
    max_load: Optional[int] = None

class LecturerResponse(LecturerBase):
    lecturer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- PROGRAMS ---
class ProgramBase(BaseModel):
    department_id: int
    name: str
    level: str

class ProgramCreate(ProgramBase):
    pass

class ProgramUpdate(BaseModel):
    department_id: Optional[int] = None
    name: Optional[str] = None
    level: Optional[str] = None

class ProgramResponse(ProgramBase):
    program_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- COURSES ---
class CourseBase(BaseModel):
    department_id: int
    course_code: str
    title: str
    credit_hour: int = Field(..., gt=0)
    course_type: str = "lecture"

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    department_id: Optional[int] = None
    course_code: Optional[str] = None
    title: Optional[str] = None
    credit_hour: Optional[int] = Field(None, gt=0)
    course_type: Optional[str] = None

class CourseResponse(CourseBase):
    course_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- SECTIONS ---
class SectionBase(BaseModel):
    program_id: int
    name: str
    capacity: int = Field(..., gt=0)

class SectionCreate(SectionBase):
    pass

class SectionUpdate(BaseModel):
    program_id: Optional[int] = None
    name: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)

class SectionResponse(SectionBase):
    section_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- ACADEMIC YEARS ---
class AcademicYearBase(BaseModel):
    label: str

class AcademicYearCreate(AcademicYearBase):
    pass

class AcademicYearUpdate(BaseModel):
    label: Optional[str] = None

class AcademicYearResponse(AcademicYearBase):
    academic_year_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- SEMESTERS ---
class SemesterBase(BaseModel):
    academic_year_id: int
    name: str

class SemesterCreate(SemesterBase):
    pass

class SemesterUpdate(BaseModel):
    academic_year_id: Optional[int] = None
    name: Optional[str] = None

class SemesterResponse(SemesterBase):
    semester_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- TIME SLOTS ---
class TimeSlotBase(BaseModel):
    day: str
    start_time: time
    end_time: time

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlotUpdate(BaseModel):
    day: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class TimeSlotResponse(TimeSlotBase):
    slot_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- COURSE OFFERINGS ---
# A specific course, taught by a specific lecturer, to a specific section,
# in a specific semester -- the thing that actually gets scheduled.
class CourseOfferingBase(BaseModel):
    course_id: int
    semester_id: int
    lecturer_id: int
    section_id: int

class CourseOfferingCreate(CourseOfferingBase):
    pass

class CourseOfferingUpdate(BaseModel):
    course_id: Optional[int] = None
    semester_id: Optional[int] = None
    lecturer_id: Optional[int] = None
    section_id: Optional[int] = None

class CourseOfferingResponse(CourseOfferingBase):
    offering_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- LECTURER AVAILABILITY ---
# Nested under a specific lecturer (/api/lecturers/{lecturer_id}/availability)
# -- lecturer_id deliberately isn't on Create/Update, since it comes from
# the URL path, not the request body. See LecturerAvailabilityResponse for
# where it does appear, since the client does need to see it in reads.
class LecturerAvailabilityBase(BaseModel):
    day: str
    start_time: time
    end_time: time
    available: bool = True

class LecturerAvailabilityCreate(LecturerAvailabilityBase):
    pass

class LecturerAvailabilityUpdate(BaseModel):
    day: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    available: Optional[bool] = None

class LecturerAvailabilityResponse(LecturerAvailabilityBase):
    availability_id: int
    lecturer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True