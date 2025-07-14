from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.notifications import Notification
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.services.notification import notification_service
from main import app


def mock_get_current_user():
    return User(
        id=str(uuid7().hex),
        email="user@gmail.com",
        password=user_service.hash_password("Testuser@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_notification():
    return Notification(
        id=str(uuid7().hex),
        title="TTest qustion?",
        message="TAnswer"
    )


@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_mark_notification_as_read_success(client, db_session_mock):
    '''Test to successfully fetch a new notification'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user
    app.dependency_overrides[notification_service.mark_notification_as_read] = None

    # Mock notification creation
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_nots = mock_notification()

    with patch("api.v1.services.notification.notification_service.mark_notification_as_read", return_value=None) as mock_mark_notification_as_read:
        response = client.patch(
            f'/api/v1/notifications/{mock_nots.id}/mark-as-read',
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 200


def test_notification_not_found(client, db_session_mock):
    """Test when the notification ID does not exist."""

    # Mock the user service to return the current super admin user
    app.dependency_overrides[user_service.get_current_user] = mock_get_current_user
    app.dependency_overrides[notification_service.mark_notification_as_read] = None

    # Simulate a non-existent organisation
    nonexistent_id = str(uuid7().hex)

    # Mock the organisation service to raise an exception for a non-existent notification
    with patch("api.v1.services.notification.notification_service.mark_notification_as_read", side_effect=HTTPException(status_code=404, detail="Notification not found")):
        response = client.patch(
            f'/api/v1/notifications/{nonexistent_id}/mark-as-read',
            headers={'Authorization': 'Bearer valid_token'}
        )

        # Assert that the response status code is 404 Not Found
        assert response.status_code == 404
