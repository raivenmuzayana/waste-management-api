from fastapi.testclient import TestClient

def test_create_location(client: TestClient, admin_auth_headers):
    response = client.post(
        "/locations/",
        headers=admin_auth_headers,
        json={"name": "Lokasi Tes 1", "latitude": -6.917, "longitude": 107.619}
    )
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["name"] == "Lokasi Tes 1"
    assert "id" in json_data

def test_create_location_duplicate(client: TestClient, admin_auth_headers):
    # Buat yang pertama
    client.post(
        "/locations/",
        headers=admin_auth_headers,
        json={"name": "Lokasi Duplikat", "latitude": 0, "longitude": 0}
    )
    # Buat yang kedua (gagal)
    response = client.post(
        "/locations/",
        headers=admin_auth_headers,
        json={"name": "Lokasi Duplikat", "latitude": 0, "longitude": 0}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Location name already exists"

def test_get_locations(client: TestClient, admin_auth_headers):
    response = client.get("/locations/", headers=admin_auth_headers)
    assert response.status_code == 200