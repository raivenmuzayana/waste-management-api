from fastapi.testclient import TestClient
from datetime import datetime

def test_create_collection_record(client: TestClient, admin_auth_headers):
	# Buat lokasi dan kategori lewat endpoint (mirip style test_location)
	loc_resp = client.post(
		"/locations/",
		headers=admin_auth_headers,
		json={"name": "Lokasi Uji", "latitude": -6.0, "longitude": 107.0}
	)
	assert loc_resp.status_code == 201
	loc = loc_resp.json()

	cat_resp = client.post(
		"/categories/",
		headers=admin_auth_headers,
		json={"name": "Organik", "description": "Bahan organik"}
	)
	assert cat_resp.status_code == 201
	cat = cat_resp.json()

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
	# Buat sampel lewat endpoints
	loc = client.post("/locations/", headers=admin_auth_headers, json={"name": "Lokasi X", "latitude": -6.0, "longitude": 107.0}).json()
	cat = client.post("/categories/", headers=admin_auth_headers, json={"name": "Anorganik", "description": "Sampah keras"}).json()

	payload = {"volume_kg": 5.0, "collection_date": datetime.now().isoformat(), "location_id": loc["id"], "category_id": cat["id"]}
	client.post("/collections/", json=payload)

	response = client.get("/collections/")
	assert response.status_code == 200
	json_data = response.json()
	assert isinstance(json_data, list)
	assert len(json_data) >= 1


def test_get_specific_collection_record(client: TestClient, admin_auth_headers):
	loc = client.post("/locations/", headers=admin_auth_headers, json={"name": "Lokasi Cek", "latitude": -6.0, "longitude": 107.0}).json()
	cat = client.post("/categories/", headers=admin_auth_headers, json={"name": "Campuran", "description": "Mixed waste"}).json()

	payload = {"volume_kg": 9.0, "collection_date": datetime.now().isoformat(), "location_id": loc["id"], "category_id": cat["id"]}
	created = client.post("/collections/", json=payload).json()

	response = client.get(f"/collections/{created['id']}")
	assert response.status_code == 200
	json_data = response.json()
	assert json_data["id"] == created["id"]
	assert json_data["location_id"] == loc["id"]
	assert json_data["category_id"] == cat["id"]


def test_record_not_found(client: TestClient):
	response = client.get("/collections/99999")
	assert response.status_code == 404
	assert response.json()["detail"] == "Catatan tidak ditemukan"

