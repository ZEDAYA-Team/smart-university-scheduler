def test_create_and_get_faculty(client):
    # Test valid creation (201)
    response = client.post(
        "/api/setup/faculties",
        json={"name": "College of Natural Sciences", "code": "CNCS"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "CNCS"
    assert "faculty_id" in data

    # Test listing faculties (200)
    list_response = client.get("/api/setup/faculties")
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

def test_faculty_validation_error(client):
    # Missing required field 'code' should return 422
    response = client.post(
        "/api/setup/faculties",
        json={"name": "Incomplete Faculty"}
    )
    assert response.status_code == 422

def test_room_capacity_validation(client):
    # First create a building
    b_res = client.post("/api/setup/buildings", json={"name": "Block 10"})
    building_id = b_res.json()["building_id"]

    # Capacity <= 0 should fail with 422 due to Field(..., gt=0)
    response = client.post(
        "/api/setup/rooms",
        json={
            "building_id": building_id,
            "room_number": "101",
            "capacity": -5,
            "room_type": "lecture"
        }
    )
    assert response.status_code == 422