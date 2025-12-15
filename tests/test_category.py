def test_read_categories_success(client, admin_auth_headers):
    response = client.get(
        "/categories/",
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_category_not_found(client, admin_auth_headers):
    response = client.get(
        "/categories/999999",
        headers=admin_auth_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"

def test_read_category_by_id_success(client, db_session, admin_auth_headers):
    from models.category_model import WasteCategory

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

def test_create_category(client, admin_token):
    # Tes Create (Butuh Admin)
    response = client.post(
        "/categories/",
        json={"name": "Elektronik", "description": "Sampah gadget"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 201 
    
    assert response.json()["name"] == "Elektronik"

def test_get_categories(client, admin_token):
    # Tes Read
    response = client.get("/categories/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)