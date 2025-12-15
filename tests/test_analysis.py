from fastapi.testclient import TestClient
from datetime import datetime
import uuid
from models.category_model import WasteCategory

#unique string generator
def unique(name: str):
    return f"{name}_{uuid.uuid4().hex[:6]}"

def setup_dummy_data(client: TestClient, db_session, admin_auth_headers):
    # Buat dua lokasi
    l1 = client.post("/locations/", headers=admin_auth_headers, json={"name": unique("L1"), "latitude": -6.0, "longitude": 107.0}).json()
    l2 = client.post("/locations/", headers=admin_auth_headers, json={"name": unique("L2"), "latitude": -6.0, "longitude": 108.0}).json()

    # Buat dua kategori via DB session
    c1 = WasteCategory(name=unique("Organik"), description="")
    c2 = WasteCategory(name=unique("Anorganik"), description="")

    db_session.add_all([c1, c2])
    db_session.commit()
    db_session.refresh(c1)
    db_session.refresh(c2)

    # Create collection records
    now = datetime.now().isoformat()

    # Data untuk analisis
    client.post("/collections/", json={
        "volume_kg": 10.0,
        "collection_date": now,
        "location_id": l1["id"],
        "category_id": c1.id
    })
    client.post("/collections/", json={
        "volume_kg": 30.0,
        "collection_date": now,
        "location_id": l2["id"],
        "category_id": c2.id
    })


# ---------- tests ----------

def test_avg_volume_by_location(client: TestClient, db_session, admin_auth_headers):
    setup_dummy_data(client, db_session, admin_auth_headers)

    response = client.get("/analysis/avg-volume/by-location", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "location_name" in data[0]
    assert "average_volume" in data[0]


def test_avg_volume_by_category(client: TestClient, db_session, admin_auth_headers):
    setup_dummy_data(client, db_session, admin_auth_headers)

    response = client.get("/analysis/avg-volume/by-category", headers=admin_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_top_locations(client: TestClient, db_session, admin_auth_headers):
    setup_dummy_data(client, db_session, admin_auth_headers)

    response = client.get("/analysis/top-locations", headers=admin_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_category_distribution(client: TestClient, db_session, admin_auth_headers):
    setup_dummy_data(client, db_session, admin_auth_headers)

    response = client.get("/analysis/distribution", headers=admin_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_daily_trend(client: TestClient, db_session, admin_auth_headers):
    setup_dummy_data(client, db_session, admin_auth_headers)

    response = client.get("/analysis/trend/daily", headers=admin_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_prediction_placeholder(client: TestClient, admin_auth_headers):
    response = client.get("/analysis/prediction", headers=admin_auth_headers)
    assert response.status_code == 200
    json_data = response.json()

    if json_data.get("status") == "error":
        assert "Data tidak cukup" in json_data.get("message")
    else:
        assert "predictions" in json_data
        assert "trend_analysis" in json_data

def test_top_producing_days(client: TestClient, db_session, admin_auth_headers):
    setup_dummy_data(client, db_session, admin_auth_headers)

    response = client.get("/analysis/top-days", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    if len(data) > 0:
        assert "day_name" in data[0]
        assert "total_volume" in data[0]
        assert "percentage" in data[0]
