# tests/test_auth.py
def test_register_success(client):
    response = client.post("/api/auth/register", json={
        "email": "new@example.com",
        "password": "password123",
        "company_name": "New Corp",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={
        "email": "dupe@example.com",
        "password": "password123",
    })
    response = client.post("/api/auth/register", json={
        "email": "dupe@example.com",
        "password": "password456",
    })
    assert response.status_code == 409


def test_register_short_password(client):
    response = client.post("/api/auth/register", json={
        "email": "short@example.com",
        "password": "short",
    })
    assert response.status_code == 422


def test_login_success(client):
    client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "password123",
    })
    response = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "password123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "email": "wrong@example.com",
        "password": "password123",
    })
    response = client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpass",
    })
    assert response.status_code == 401


def test_protected_endpoint_without_token(client):
    response = client.get("/api/widgets")
    assert response.status_code == 403  # No auth header