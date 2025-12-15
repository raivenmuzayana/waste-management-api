from fastapi.testclient import TestClient
from models import user_model, category_model
from services import auth_service

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

def test_delete_location_forbidden_for_analyst(client: TestClient, db_session, admin_auth_headers):
    #ngetes delete lokasi pake user selain admin (should be er code 403)
    analyst_user = user_model.User(
        username="analyst_tester",
        hashed_password=auth_service.get_password_hash("pass123"),
        role=user_model.UserRole.DATA_ANALYST
    )
    db_session.add(analyst_user)
    db_session.commit() 
    
    token = auth_service.create_access_token(data={"sub": analyst_user.username})
    analyst_headers = {"Authorization": f"Bearer {token}"}

    loc_created = client.post(
        "/locations/",
        headers=admin_auth_headers,
        json={"name": "Lokasi Khusus Admin", "latitude": 0, "longitude": 0}
    ).json()

    response = client.delete(
        f"/locations/{loc_created['id']}",
        headers=analyst_headers
    )

    #Validasi sesuai logic router (Source: auth_service.py)
    assert response.status_code == 403
    assert "Operation not permitted" in response.json()["detail"]


def test_delete_used_location_should_fail(client: TestClient, db_session, admin_auth_headers):
    #ngetes hapus lokasi yang udah dipakai di collection record
    loc_res = client.post(
        "/locations/",
        headers=admin_auth_headers,
        json={"name": "Lokasi Terpakai", "latitude": -6.1, "longitude": 106.8}
    ).json()

    cat = category_model.WasteCategory(
        name="Kategori Tes Constraint", 
        description="Untuk tes hapus"
    )
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)

    client.post(
        "/collections/",
        headers=admin_auth_headers,
        json={
            "volume_kg": 50.5,
            "location_id": loc_res["id"],
            "category_id": cat.id
        }
    )

    response = client.delete(
        f"/locations/{loc_res['id']}",
        headers=admin_auth_headers
    )

    assert response.status_code == 400
    assert response.json()["detail"]