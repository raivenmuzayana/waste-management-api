from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import user_model

def test_admin_login(client: TestClient, test_admin_user):
    response = client.post(
        "/auth/login",
        data={"username": "testadmin", "password": "password123"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_get_me(client: TestClient, admin_auth_headers):
    response = client.get("/auth/me", headers=admin_auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["username"] == "testadmin"
    assert json_data["role"] == "admin"

def test_delete_category_as_analyst_fail(client, analyst_token):
    response = client.delete("/categories/1", headers={"Authorization": f"Bearer {analyst_token}"})
    assert response.status_code == 403 # Harus Forbidden