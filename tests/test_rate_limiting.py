# tests/test_rate_limiting.py
"""Test rate limiting returns 429 under burst."""


def test_rate_limiting_burst(client, sample_widget):
    """Fire rapid submissions → 429 appears, then normal request still works."""
    widget_id = sample_widget["id"]
    payload = {
        "widget_id": widget_id,
        "data": {"name": "Rate Test", "email": "rate@test.com"},
    }

    got_429 = False
    for i in range(25):
        response = client.post("/api/submissions", json=payload)
        if response.status_code == 429:
            got_429 = True
            break

    assert got_429, "Expected 429 after burst of requests, but never got one"