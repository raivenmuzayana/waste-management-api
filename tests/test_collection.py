from fastapi.testclient import TestClient
from datetime import datetime
import uuid

# Fungsi bantu untuk bikin nama unik (agar tidak error Duplicate Entry)
def generate_unique_name(prefix: str):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def test_create_collection_record(client: TestClient, admin_auth_headers):
    # 1. Buat Lokasi dengan nama UNIK
    unique_loc = generate_unique_name("Lokasi Uji")
    loc_resp = client.post(
        "/locations/",
        headers=admin_auth_headers,
        json={"name": unique_loc, "latitude": -6.0, "longitude": 107.0}
    )
    assert loc_resp.status_code == 201
    loc = loc_resp.json()

    # 2. Buat Kategori dengan nama UNIK
    unique_cat = generate_unique_name("Kategori Uji")
    cat_resp = client.post(
        "/categories/",
        headers=admin_auth_headers,
        json={"name": unique_cat, "description": "Bahan tes"}
    )
    assert cat_resp.status_code == 201
    cat = cat_resp.json()

    # 3. Buat Collection Record
    payload = {
        "volume_kg": 12.5,
        "collection_date": datetime.now().isoformat(),
        "location_id": loc["id"],
        "category_id": cat["id"],
    }

    response = client.post("/collections/", json=payload)
    assert response.status_code == 201
    json_data = response.json()
    
    assert json_data["volume_kg"] == payload["volume_kg"]
    assert json_data["location_id"] == loc["id"]
    assert json_data["category_id"] == cat["id"]
    assert "id" in json_data


def test_get_collection_records(client: TestClient, admin_auth_headers):
    # Buat sampel lewat endpoints (Pakai nama unik lagi)
    loc_name = generate_unique_name("Lokasi X")
    cat_name = generate_unique_name("Kategori X")

    loc = client.post("/locations/", headers=admin_auth_headers, json={"name": loc_name, "latitude": -6.0, "longitude": 107.0}).json()
    cat = client.post("/categories/", headers=admin_auth_headers, json={"name": cat_name, "description": "Tes"}).json()

    payload = {"volume_kg": 5.0, "collection_date": datetime.now().isoformat(), "location_id": loc["id"], "category_id": cat["id"]}
    client.post("/collections/", json=payload)

    # Test GET
    response = client.get("/collections/")
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)
    assert len(json_data) >= 1


def test_get_specific_collection_record(client: TestClient, admin_auth_headers):
    # Pakai nama unik lagi
    loc_name = generate_unique_name("Lokasi Cek")
    cat_name = generate_unique_name("Kategori Cek")

    loc = client.post("/locations/", headers=admin_auth_headers, json={"name": loc_name, "latitude": -6.0, "longitude": 107.0}).json()
    cat = client.post("/categories/", headers=admin_auth_headers, json={"name": cat_name, "description": "Tes"}).json()

    payload = {"volume_kg": 9.0, "collection_date": datetime.now().isoformat(), "location_id": loc["id"], "category_id": cat["id"]}
    created = client.post("/collections/", json=payload).json()

    response = client.get(f"/collections/{created['id']}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["id"] == created["id"]
    assert json_data["location_id"] == loc["id"]
    assert json_data["category_id"] == cat["id"]


def test_record_not_found(client: TestClient):
    # ID ngawur yang pasti gak ada
    response = client.get("/collections/99999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Catatan tidak ditemukan"