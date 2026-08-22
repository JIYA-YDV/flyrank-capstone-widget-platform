# tests/test_side_effects.py
"""Test that failing email/webhook does not block submission."""
from unittest.mock import patch


def test_email_failure_does_not_block_submission(client, sample_widget):
    """Break the email side effect → submission still succeeds."""
    widget_id = sample_widget["id"]

    with patch(
        "app.services.notification_service.notification_service.send_submission_notification",
        side_effect=Exception("SMTP server exploded!"),
    ):
        response = client.post(
            "/api/submissions",
            json={
                "widget_id": widget_id,
                "data": {"name": "Side Effect Test", "email": "side@test.com"},
            },
        )
        # Submission must still succeed despite email failure
        assert response.status_code == 201
        assert response.json()["data"]["name"] == "Side Effect Test"