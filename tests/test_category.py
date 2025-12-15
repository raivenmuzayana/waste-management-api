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