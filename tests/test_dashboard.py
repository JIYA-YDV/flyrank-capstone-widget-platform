# tests/test_dashboard.py
def test_dashboard_submissions(client, auth_headers, sample_widget):
    """Dashboard returns submissions for the authenticated owner."""
    widget_id = sample_widget["id"]

    # Create a submission first
    client.post(
        "/api/submissions",
        json={
            "widget_id": widget_id,
            "data": {"name": "Dashboard Test", "email": "dash@test.com"},
        },
    )

    response = client.get("/api/dashboard/submissions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["submissions"]) >= 1


def test_dashboard_stats(client, auth_headers, sample_widget):
    """Dashboard stats endpoint returns aggregated data."""
    widget_id = sample_widget["id"]

    # Create submissions
    for i in range(3):
        client.post(
            "/api/submissions",
            json={
                "widget_id": widget_id,
                "data": {"name": f"Stats User {i}", "email": f"stats{i}@test.com"},
            },
        )

    response = client.get("/api/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_submissions"] >= 3
    assert "by_widget" in data
    assert "by_country" in data


def test_dashboard_tenant_isolation(client, auth_headers, sample_widget):
    """User B cannot see User A's submissions in the dashboard."""
    widget_id = sample_widget["id"]

    # Submit as public
    client.post(
        "/api/submissions",
        json={
            "widget_id": widget_id,
            "data": {"name": "Isolated", "email": "iso@test.com"},
        },
    )

    # Register second user
    client.post("/api/auth/register", json={
        "email": "userb_dash@example.com",
        "password": "password123",
    })
    login_resp = client.post("/api/auth/login", json={
        "email": "userb_dash@example.com",
        "password": "password123",
    })
    headers_b = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # User B's dashboard should be empty
    response = client.get("/api/dashboard/submissions", headers=headers_b)
    assert response.status_code == 200
    assert response.json()["total"] == 0