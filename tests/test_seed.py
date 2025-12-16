def test_generate_dummy_data(client, db_session):
    # Default generate 100 data
    response = client.post("/seed/generate-dummy-data?jumlah_data=10")
    assert response.status_code == 200
    data = response.json()
    assert data["detail"]["records_created"] == 10