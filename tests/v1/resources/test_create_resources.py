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
def client():
    client = TestClient(app)
    yield client


test_resource_req_body = {
    "title": "TTest title?",
    "content": "TAnswer",
    "image_url": "random.com",
}


class TestCodeUnderTest:
    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_create_resource_success(self, client):
        """Test to successfully create a new resource"""

        # Mock the user service to return the current user
        app.dependency_overrides[user_service.get_current_super_admin] = (
            lambda: MagicMock()
        )

        mock_freq_asked_titles = mock_resource()

        with patch(
            "api.v1.services.resource.resource_service.create",
            return_value=mock_resource(),
        ) as mock_create:
            response = client.post("/api/v1/resources", data=test_resource_req_body)

            print(response.json())

            assert response.status_code == 201
            assert response.json()["data"]["title"] == mock_freq_asked_titles.title
            assert response.json()["data"]["content"] == mock_freq_asked_titles.content

    def test_create_resource_missing_field(self, client, db_session_mock):
        """Test for missing field when creating a new resource"""

        # Mock the user service to return the current admin
        app.dependency_overrides[user_service.get_current_super_admin] = (
            lambda: MagicMock()
        )

        mock_freq_asked_titles = mock_resource()

        with patch(
            "api.v1.services.resource.resource_service.create",
            return_value=mock_freq_asked_titles,
        ) as mock_create:
            response = client.post(
                "/api/v1/resources", data={"title": "TTest qustion?"}
            )

            assert response.status_code == 422

    def test_create_resource_forbidden(self, client, db_session_mock):
        """Test unauthourized user

        Args:
            client: TestClient object
            db_session_mock (MagicMock):
        """
        app.dependency_overrides = {}
        app.dependency_overrides[get_db] = lambda: db_session_mock
        app.dependency_overrides[oauth2_scheme] = lambda: "access_token"

        with patch(
            "api.v1.services.user.user_service.get_current_user",
            return_value=MagicMock(is_superadmin=False),
        ) as cu:
            response = client.post("/api/v1/resources", data=test_resource_req_body)

        assert response.status_code == 403
        assert (
            response.json()["message"]
            == "You do not have permission to access this resource"
        )
