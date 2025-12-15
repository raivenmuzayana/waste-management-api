from fastapi.testclient import TestClient
from datetime import datetime
import uuid
from models.location_model import Location
from models.category_model import WasteCategory
from models.collection_model import CollectionRecord

# Fungsi bantu untuk bikin nama unik
def generate_unique_name(prefix: str):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def create_location_and_category(db_session):
    location = Location(
        name=generate_unique_name("Lokasi Test"),
        latitude=-6.0,
        longitude=107.0
    )

    category = WasteCategory(
        name=generate_unique_name("Kategori Test"),
        description="Kategori untuk testing"
    )

    db_session.add_all([location, category])
    db_session.commit()
    db_session.refresh(location)
    db_session.refresh(category)

    return location, category


def test_create_collection_record(client: TestClient, db_session):
    location, category = create_location_and_category(db_session)

    payload = {
        "volume_kg": 12.5,
        "collection_date": datetime.now().isoformat(),
        "location_id": location.id,
        "category_id": category.id
    }

    response = client.post("/collections/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["volume_kg"] == payload["volume_kg"]
    assert data["location"]["id"] == location.id
    assert data["waste_category"]["id"] == category.id
    assert "id" in data


def test_get_collection_records(client: TestClient, db_session):
    location, category = create_location_and_category(db_session)

    client.post("/collections/", json={
        "volume_kg": 5.0,
        "location_id": location.id,
        "category_id": category.id
    })

    response = client.get("/collections/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_specific_collection_record(client: TestClient, db_session):
    location, category = create_location_and_category(db_session)

    created = client.post("/collections/", json={
        "volume_kg": 9.0,
        "location_id": location.id,
        "category_id": category.id
    }).json()

    response = client.get(f"/collections/{created['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == created["id"]
    assert data["location"]["id"] == location.id
    assert data["waste_category"]["id"] == category.id

def test_update_collection_record(client: TestClient, db_session, admin_auth_headers):
    location, category = create_location_and_category(db_session)
    
    record = CollectionRecord(
        volume_kg=10.0,
        location_id=location.id,
        category_id=category.id,
        collection_date=datetime.now()
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)

    update_payload = {
        "volume_kg": 50.0
    }

    response = client.put(
        f"/collections/{record.id}",
        headers=admin_auth_headers,
        json=update_payload
    )

    assert response.status_code == 200
    data = response.json()
    assert data["volume_kg"] == 50.0
    assert data["id"] == record.id


def test_delete_collection_record(client: TestClient, db_session):
    location, category = create_location_and_category(db_session)
    
    created = client.post("/collections/", json={
        "volume_kg": 5.5,
        "location_id": location.id,
        "category_id": category.id
    }).json()

    response = client.delete(f"/collections/{created['id']}")
    assert response.status_code == 204 

    check_response = client.get(f"/collections/{created['id']}")
    assert check_response.status_code == 404

def test_collection_not_found(client: TestClient):
    response = client.get("/collections/99999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Catatan tidak ditemukan"