from fastapi.testclient import TestClient


def test_create_location(client: TestClient, admin_auth_headers):
    response = client.post(
        "/locations/",
        headers=admin_auth_headers,
        json={"name": "Lokasi Tes 1", "latitude": -6.917, "longitude": 107.619}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Lokasi Tes 1"
    assert "id" in data


def test_create_location_duplicate(client: TestClient, admin_auth_headers):
    client.post(
        "/locations/",
        headers=admin_auth_headers,
        json={"name": "Lokasi Duplikat", "latitude": 0, "longitude": 0}
    )

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
    assert isinstance(response.json(), list)


def test_get_location_by_id(client: TestClient, admin_auth_headers):
    created = client.post(
        "/locations/",
        headers=admin_auth_headers,
        json={"name": "Lokasi Detail", "latitude": 1.1, "longitude": 2.2}
    ).json()

    response = client.get(
        f"/locations/{created['id']}",
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_update_location_admin_only(client: TestClient, admin_auth_headers):
    created = client.post(
        "/locations/",
        headers=admin_auth_headers,
        json={"name": "Lokasi Update", "latitude": 0, "longitude": 0}
    ).json()

    response = client.put(
        f"/locations/{created['id']}",
        headers=admin_auth_headers,
        json={"name": "Lokasi Update Baru"}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Lokasi Update Baru"


def test_delete_location_admin_only(client: TestClient, admin_auth_headers):
    created = client.post(
        "/locations/",
        headers=admin_auth_headers,
        json={"name": "Lokasi Hapus", "latitude": 0, "longitude": 0}
    ).json()

    response = client.delete(
        f"/locations/{created['id']}",
        headers=admin_auth_headers
    )

    assert response.status_code == 204


def test_location_not_found(client: TestClient, admin_auth_headers):
    response = client.get(
        "/locations/999999",
        headers=admin_auth_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Location not found"