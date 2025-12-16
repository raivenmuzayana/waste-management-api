from fastapi.testclient import TestClient
from models.category_model import WasteCategory

def test_read_categories_success(client: TestClient, admin_auth_headers):
    response = client.get(
        "/categories/",
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_category_not_found(client: TestClient, admin_auth_headers):
    response = client.get(
        "/categories/999999",
        headers=admin_auth_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"

def test_read_category_by_id_success(client: TestClient, db_session, admin_auth_headers):

    category = WasteCategory(
        name="Kategori Test Read",
        description="Untuk testing get by id"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    response = client.get(
        f"/categories/{category.id}",
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category.id
    assert data["name"] == category.name

def test_create_category(client: TestClient, admin_auth_headers):
    # Tes Create (Butuh Admin)
    response = client.post(
        "/categories/",
        json={"name": "Elektronik", "description": "Sampah gadget"},
        headers=admin_auth_headers 
    )
    
    assert response.status_code == 201 
    assert response.json()["name"] == "Elektronik"

#tes duplikat
def test_create_category_duplicate_fails(client: TestClient, db_session, admin_auth_headers):
    # Setup: Create a category first
    category = WasteCategory(name="Duplikat", description="Awal")
    db_session.add(category)
    db_session.commit()

    response = client.post(
        "/categories/",
        json={"name": "Duplikat", "description": "Baru"},
        headers=admin_auth_headers
    )

    # Assert: Should fail with 400 Bad Request
    assert response.status_code == 400
    assert response.json()["detail"] == "Category name already exists"

#tes read diapus (==get categories)
#tes update, delete admin
def test_update_category_admin_only(client: TestClient, db_session, admin_auth_headers):
    category = WasteCategory(name="Kategori Lama", description="Old")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    response = client.put(
        f"/categories/{category.id}",
        headers=admin_auth_headers,
        json={"name": "Kategori Baru"}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Kategori Baru"

def test_update_category_unauthorized(client: TestClient, db_session):
    category = WasteCategory(name="Jangan Diubah", description="Original")
    db_session.add(category)
    db_session.commit()

    response = client.put(
        f"/categories/{category.id}",
        json={"name": "Hacked Name"}
    )

    assert response.status_code == 401
    db_session.refresh(category)
    assert category.name == "Jangan Diubah"

def test_delete_category_admin_only(client: TestClient, db_session, admin_auth_headers):
    category = WasteCategory(name="Kategori Hapus", description="")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    response = client.delete(
        f"/categories/{category.id}",
        headers=admin_auth_headers
    )

    assert response.status_code == 204

def test_delete_category_unauthorized(client: TestClient, db_session):
    category = WasteCategory(name="Secure Category", description="")
    db_session.add(category)
    db_session.commit()

    response = client.delete(f"/categories/{category.id}")

    assert response.status_code == 401