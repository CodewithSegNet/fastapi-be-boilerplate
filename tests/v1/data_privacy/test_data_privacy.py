from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from fastapi import HTTPException


import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.data_privacy import DataPrivacySetting
from api.v1.services.data_privacy import data_privacy_service
from main import app


def mock_get_current_user():
    return User(
        id=str(uuid7().hex),
        email="test@gmail.com",
        password=user_service.hash_password("Testuser@123"),
        first_name='Test',
        last_name='User',
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_privacy_settings():
    return DataPrivacySetting(
        id=str(uuid7().hex),
        user_id=mock_get_current_user().id,
        profile_visibility=True,
        share_data_with_partners=False,
        receice_email_updates=True,
        enable_two_factor_authentication=True,
        use_data_encryption=True,
        allow_analytics=True,
        personalized_ads=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
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



def test_unauthorized_user(client, db_session_mock):
    '''Test for unauthorized user trying to update data privacy settings'''

    response = client.get(
        '/api/v1/data-privacy-settings',
    )

    assert response.status_code == 401
    
    
    
def test_fetch_data_privacy_settings(client, db_session_mock):
    '''Test to successfully fetch a user's data privacy settings'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()
    app.dependency_overrides[data_privacy_service.fetch] = lambda db, user: mock_privacy_settings()

    mock_privacy_setting = mock_privacy_settings()

    with patch(
        "api.v1.services.data_privacy.data_privacy_service.fetch",
        return_value=mock_privacy_setting
    ) as mock_fetch:
        
        response = client.get(
            '/api/v1/data-privacy-settings',
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 200


def test_fetch_data_privacy_settings_unauthorized(client, db_session_mock):
    '''Test for unauthorized user trying to fetch data privacy settings'''

    response = client.get(
        '/api/v1/data-privacy-settings',
    )

    assert response.status_code == 401
