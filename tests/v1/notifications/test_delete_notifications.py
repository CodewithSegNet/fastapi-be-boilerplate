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


def test_delete_notification_success(client, db_session_mock):
    '''Test to successfully delete a notification'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user
    app.dependency_overrides[notification_service.delete] = None

    mock_nots = mock_notification()

    with patch("api.v1.services.notification.notification_service.delete", return_value=None) as mock_delete:
        response = client.delete(
            f'/api/v1/notifications/{mock_nots.id}',
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 204


def test_notification_not_found(client, db_session_mock):
    """Test when the notification ID does not exist."""

    # Mock the user service to return the current super admin user
    app.dependency_overrides[user_service.get_current_user] = mock_get_current_user
    app.dependency_overrides[notification_service.delete] = None

    # Simulate a non-existent organisation
    nonexistent_id = str(uuid7().hex)

    # Mock the organisation service to raise an exception for a non-existent notification
    with patch("api.v1.services.notification.notification_service.delete", side_effect=HTTPException(status_code=404, detail="Notification not found")):
        response = client.delete(
            f'/api/v1/notifications/{nonexistent_id}',
            headers={'Authorization': 'Bearer valid_token'}
        )

        # Assert that the response status code is 404 Not Found
        assert response.status_code == 404


def test_delete_all_notifications(client, db_session_mock):
    """Test delete all user notifications."""

    # Mock the user service to return the current super admin user
    app.dependency_overrides[user_service.get_current_user] = mock_get_current_user
    app.dependency_overrides[notification_service.delete_all] = None

    # Mock the organisation service to raise an exception for a non-existent notification
    with patch("api.v1.services.notification.notification_service.delete_all", return_value=None):
        response = client.delete(
            f'/api/v1/notifications',
            headers={'Authorization': 'Bearer valid_token'}
        )

        # Assert that the response status code is 404 Not Found
        assert response.status_code == 204
