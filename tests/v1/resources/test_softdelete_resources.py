from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import oauth2_scheme, user_service
from api.v1.models.resource import Resource
from main import app


def mock_resource():
    return Resource(
        id=str(uuid7().hex),
        title="TTest title?",
        content="TAnswer",
        image_url="random.com",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    yield db_session

@pytest.fixture 
def mock_user():
    return lambda : MagicMock()

client = TestClient(app)

def test_delete_resources(db_session_mock, mock_user):
    """Test to Soft delete resources

    Args:
        db_session_mock (pytest.fixture): pytest fixture
        mock_user (pytest.fixture): pytest fixture
    """
    app.dependency_overrides[user_service.get_current_super_admin] = mock_user
    app.dependency_overrides[get_db] = lambda : db_session_mock
    resource = mock_resource()
    db_session_mock.get.return_value = resource
    response = client.delete(f'/api/v1/resources/{resource.id}')
    assert response.status_code == 204
