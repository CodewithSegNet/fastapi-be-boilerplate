from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from datetime import datetime, timezone

from api.db.database import get_db
from api.v1.models.notifications import Notification
from api.v1.models.user import User
from api.v1.services.notification import notification_service
from api.v1.services.user import user_service
from main import app


def mock_get_current_user():
    return User(
        id=str(uuid7().hex),
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

@pytest.fixture
def mock_db_session():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_get_all_user_notifications(mock_db_session, client):
    """Test to verify the pagination response for notifications."""

    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()

    # Mock data
    mock_user_notifications = [
        Notification(id='1', title="Question 1", message="Answer 1"),
        Notification(id='2', title="Question 2", message="Answer 2"),
        Notification(id='3', title="Question 3", message="Answer 3"),
    ]

    app.dependency_overrides[notification_service.fetch_all_user_notifications] = mock_user_notifications

    # Perform the GET request
    response = client.get('/api/v1/notifications')

    # Verify the response
    assert response.status_code == 200
