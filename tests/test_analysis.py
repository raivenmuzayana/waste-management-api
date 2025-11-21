from fastapi.testclient import TestClient
from datetime import datetime


def setup_dummy_data(client: TestClient, admin_auth_headers: dict):
    # Buat dua lokasi dan dua kategori lewat endpoint
    l1 = client.post("/locations/", headers=admin_auth_headers, json={"name": "L1", "latitude": -6.0, "longitude": 107.0}).json()
    l2 = client.post("/locations/", headers=admin_auth_headers, json={"name": "L2", "latitude": -6.0, "longitude": 108.0}).json()

    c1 = client.post("/categories/", headers=admin_auth_headers, json={"name": "Organik", "description": ""}).json()
    c2 = client.post("/categories/", headers=admin_auth_headers, json={"name": "Anorganik", "description": ""}).json()

    # Create collection records
    now = datetime.now().isoformat()
    client.post("/collections/", json={"volume": 10.0, "collection_date": now, "location_id": l1["id"], "category_id": c1["id"]})
    client.post("/collections/", json={"volume": 30.0, "collection_date": now, "location_id": l2["id"], "category_id": c2["id"]})


def test_avg_volume_by_location(client: TestClient, admin_auth_headers):
    setup_dummy_data(client, admin_auth_headers)

    response = client.get("/analysis/avg-volume/by-location", headers=admin_auth_headers)
    assert response.status_code == 200

    json_data = response.json()
    assert isinstance(json_data, list)
    assert any(item.get("location_name") == "L1" for item in json_data)


def test_avg_volume_by_category(client: TestClient, admin_auth_headers):
    setup_dummy_data(client, admin_auth_headers)

    response = client.get("/analysis/avg-volume/by-category", headers=admin_auth_headers)
    assert response.status_code == 200

    json_data = response.json()
    assert isinstance(json_data, list)
    assert any(item.get("category_name") == "Organik" for item in json_data)


def test_top_locations(client: TestClient, admin_auth_headers):
    setup_dummy_data(client, admin_auth_headers)

    response = client.get("/analysis/top-locations", headers=admin_auth_headers)
    assert response.status_code == 200

    json_data = response.json()
    assert isinstance(json_data, list)
    assert len(json_data) >= 1
    assert json_data[0].get("location_name") in ("L1", "L2")


def test_category_distribution(client: TestClient, admin_auth_headers):
    setup_dummy_data(client, admin_auth_headers)

    response = client.get("/analysis/distribution", headers=admin_auth_headers)
    assert response.status_code == 200

    json_data = response.json()
    assert isinstance(json_data, list)
    assert len(json_data) >= 1
    assert "percentage" in json_data[0]


def test_daily_trend(client: TestClient, admin_auth_headers):
    setup_dummy_data(client, admin_auth_headers)

    response = client.get("/analysis/trend/daily", headers=admin_auth_headers)
    assert response.status_code == 200

    json_data = response.json()
    assert isinstance(json_data, list)
    assert len(json_data) >= 1
    assert "collection_date" in json_data[0]


def test_prediction_placeholder(client: TestClient, admin_auth_headers):
    response = client.get("/analysis/prediction", headers=admin_auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data.get("message") == "Fitur prediksi sedang dalam pengembangan."
