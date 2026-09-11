# tests/test_availability.py

def test_lecturer_availability_end_time_validation(client, db_session):
    # 1. Create parent records to satisfy foreign keys
    fac_res = client.post("/api/setup/faculties", json={"name": "Engineering", "code": "ENG"})
    faculty_id = fac_res.json()["faculty_id"]

    dept_res = client.post(
        "/api/setup/departments", 
        json={"faculty_id": faculty_id, "name": "Computer Engineering", "code": "CE"}
    )
    dept_id = dept_res.json()["department_id"]

    # Create dummy user (or insert directly via db_session if auth user exists)
    # Ensure a lecturer row exists:
    lecturer_res = client.post(
        "/api/setup/lecturers",
        json={"user_id": 1, "department_id": dept_id, "max_load": 12}
    )
    lecturer_id = lecturer_res.json()["lecturer_id"]

    # 2. Now post invalid time window (end_time before start_time)
    response = client.post(
        f"/api/lecturers/{lecturer_id}/availability",
        json={
            "day": "Monday",
            "start_time": "10:00:00",
            "end_time": "08:00:00",
            "available": True
        }
    )
    
    # 3. Lecturer exists, so it successfully reaches validation and returns 422
    assert response.status_code == 422
    assert response.json()["detail"] == "end_time must be after start_time"