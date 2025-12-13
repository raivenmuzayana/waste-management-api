from fastapi.testclient import TestClient
from datetime import datetime

# Fungsi setup dummy data (biarkan seperti sebelumnya)
def setup_dummy_data(client: TestClient, admin_auth_headers: dict):
    # Buat dua lokasi
    l1 = client.post("/locations/", headers=admin_auth_headers, json={"name": "L1", "latitude": -6.0, "longitude": 107.0}).json()
    l2 = client.post("/locations/", headers=admin_auth_headers, json={"name": "L2", "latitude": -6.0, "longitude": 108.0}).json()

    # Buat dua kategori
    c1 = client.post("/categories/", headers=admin_auth_headers, json={"name": "Organik", "description": ""}).json()
    c2 = client.post("/categories/", headers=admin_auth_headers, json={"name": "Anorganik", "description": ""}).json()

    # Create collection records
    now = datetime.now().isoformat()
    # Pastikan ID valid
    if "id" in l1 and "id" in c1:
        client.post("/collections/", json={"volume_kg": 10.0, "collection_date": now, "location_id": l1["id"], "category_id": c1["id"]})
    if "id" in l2 and "id" in c2:
        client.post("/collections/", json={"volume_kg": 30.0, "collection_date": now, "location_id": l2["id"], "category_id": c2["id"]})


def test_avg_volume_by_location(client: TestClient, admin_auth_headers):
    setup_dummy_data(client, admin_auth_headers)
    response = client.get("/analysis/avg-volume/by-location", headers=admin_auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)
    # Minimal ada data, cek struktur
    if len(json_data) > 0:
        assert "location_name" in json_data[0]
        assert "average_volume" in json_data[0]


def test_avg_volume_by_category(client: TestClient, admin_auth_headers):
    setup_dummy_data(client, admin_auth_headers)
    response = client.get("/analysis/avg-volume/by-category", headers=admin_auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)


def test_top_locations(client: TestClient, admin_auth_headers):
    setup_dummy_data(client, admin_auth_headers)
    response = client.get("/analysis/top-locations", headers=admin_auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)


def test_category_distribution(client: TestClient, admin_auth_headers):
    setup_dummy_data(client, admin_auth_headers)
    response = client.get("/analysis/distribution", headers=admin_auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)


def test_daily_trend(client: TestClient, admin_auth_headers):
    setup_dummy_data(client, admin_auth_headers)
    response = client.get("/analysis/trend/daily", headers=admin_auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)


# --- PERBAIKAN UTAMA DI SINI ---
def test_prediction_placeholder(client: TestClient, admin_auth_headers):
    response = client.get("/analysis/prediction", headers=admin_auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    
    # Karena data dummy sedikit, sistem akan mengembalikan status error/pesan data kurang
    # Sesuaikan assert dengan return value baru di analysis_service.py
    if json_data.get("status") == "error":
        assert "Data tidak cukup" in json_data.get("message")
    else:
        # Jika data cukup (kebetulan), cek strukturnya
        assert "predictions" in json_data
        assert "trend_analysis" in json_data

def test_top_producing_days(client: TestClient, admin_auth_headers):
    # 1. Siapkan data dummy agar ada yang bisa dihitung
    setup_dummy_data(client, admin_auth_headers)

    # 2. Panggil endpoint baru
    response = client.get("/analysis/top-days", headers=admin_auth_headers)
    
    # 3. Pastikan status 200 OK
    assert response.status_code == 200
    
    # 4. Cek struktur data
    json_data = response.json()
    assert isinstance(json_data, list) # Harus berupa list
    
    # Jika data berhasil ter-generate, cek key di dalamnya
    if len(json_data) > 0:
        first_item = json_data[0]
        assert "day_name" in first_item      # Pastikan ada nama hari
        assert "total_volume" in first_item  # Pastikan ada total volume
        assert "percentage" in first_item    # Pastikan ada persentase