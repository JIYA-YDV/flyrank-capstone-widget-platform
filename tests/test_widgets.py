# tests/test_widgets.py
def test_create_widget(client, auth_headers):
    response = client.post(
        "/api/widgets",
        json={
            "name": "My Widget",
            "widget_type": "signup_form",
            "title": "Sign Up",
            "fields_config": [
                {"name": "email", "label": "Email", "field_type": "email", "required": True},
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Widget"
    assert data["widget_type"] == "signup_form"


def test_create_widget_invalid_type(client, auth_headers):
    response = client.post(
        "/api/widgets",
        json={
            "name": "Bad Widget",
            "widget_type": "invalid_type",
            "title": "Bad",
            "fields_config": [
                {"name": "email", "label": "Email", "field_type": "email", "required": True},
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_list_widgets(client, auth_headers, sample_widget):
    response = client.get("/api/widgets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_widget(client, auth_headers, sample_widget):
    widget_id = sample_widget["id"]
    response = client.get(f"/api/widgets/{widget_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == widget_id


def test_update_widget(client, auth_headers, sample_widget):
    widget_id = sample_widget["id"]
    response = client.put(
        f"/api/widgets/{widget_id}",
        json={"title": "Updated Title"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["version"] == 2  # version incremented


def test_delete_widget(client, auth_headers, sample_widget):
    widget_id = sample_widget["id"]
    response = client.delete(f"/api/widgets/{widget_id}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/api/widgets/{widget_id}", headers=auth_headers)
    assert response.status_code == 404


def test_tenant_isolation(client, auth_headers, sample_widget):
    """User B cannot see User A's widgets."""
    # Register second user
    client.post("/api/auth/register", json={
        "email": "userb@example.com",
        "password": "password123",
    })
    login_resp = client.post("/api/auth/login", json={
        "email": "userb@example.com",
        "password": "password123",
    })
    headers_b = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # User B should not see User A's widget
    widget_id = sample_widget["id"]
    response = client.get(f"/api/widgets/{widget_id}", headers=headers_b)
    assert response.status_code == 404

    # User B's list should be empty
    response = client.get("/api/widgets", headers=headers_b)
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_snippet(client, auth_headers, sample_widget):
    widget_id = sample_widget["id"]
    response = client.get(f"/api/widgets/{widget_id}/snippet", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "snippet" in data
    assert widget_id in data["snippet"]
    assert "<script" in data["snippet"]


def test_public_config_endpoint(client, sample_widget):
    """Config endpoint is public — no auth needed, includes cache headers."""
    widget_id = sample_widget["id"]
    response = client.get(f"/api/widgets/{widget_id}/config")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Contact Us"
    assert "Cache-Control" in response.headers