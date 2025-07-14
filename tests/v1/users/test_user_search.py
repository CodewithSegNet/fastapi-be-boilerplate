"""
Test for user search endpoint
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from uuid_extensions import uuid7
from fastapi import status
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service, UserService


client = TestClient(app)


ENDPOINT = "/api/v1/users"


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."

    Yields:
        MagicMock: mock database
    """

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


@pytest.fixture
def mock_user_service():
    """Fixture to create a mock user service."""

    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service


@pytest.fixture
def mock_get_current_user():
    """Fixture to create a mock current user"""
    with patch(
        "api.v1.services.user.UserService.get_current_user", autospec=True
    ) as mock_get_current_user:
        yield mock_get_current_user


@pytest.fixture
def override_get_current_super_admin():
    """Mock the get_current_super_admin dependency"""

    app.dependency_overrides[user_service.get_current_super_admin] = lambda: User(
        id=str(uuid7().hex),
        email="admintestuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="AdminTest",
        last_name="User",
        is_active=False,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


mock_users = [
    User(
        id=str(uuid7().hex),
        email="johndoeuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="John",
        last_name="Doe",
        is_active=True,
        is_superadmin=False,
        is_deleted=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
]


def test_unauthorised_access(mock_user_service: UserService, mock_db_session: Session):
    """Test for unauthorized access to endpoint."""

    response = client.get(ENDPOINT)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_non_admin_access(
    mock_get_current_user, mock_user_service: UserService, mock_db_session: Session
):
    """Test for non admin user access to endpoint"""

    mock_get_current_user.return_value = User(
        id=str(uuid7().hex),
        email="admintestuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="AdminTest",
        last_name="User",
        is_active=False,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    response = client.get(
        ENDPOINT,
        headers={"Authorization": "Bearer dummy_token"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_successful_search_correct_case(
    mock_db_session: Session,
    mock_user_service: UserService,
    override_get_current_super_admin: None,
):
    # Mocking the query chain to return the mock users list
    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.count.return_value = len(mock_users)
    query_mock.limit.return_value = query_mock
    query_mock.offset.return_value.all.return_value = mock_users

    # Setting the mock session to use the mocked query
    mock_db_session.query.return_value = query_mock

    response = client.get(ENDPOINT, params={"search": "John"})

    print(response.json())
    assert response.status_code == 200

def test_successful_search_incorrect_case(
    mock_db_session: Session,
    mock_user_service: UserService,
    override_get_current_super_admin: None,
):
    # Mocking the query chain to return the mock users list
    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.count.return_value = len(mock_users)
    query_mock.limit.return_value = query_mock
    query_mock.offset.return_value.all.return_value = mock_users

    # Setting the mock session to use the mocked query
    mock_db_session.query.return_value = query_mock

    response = client.get(ENDPOINT, params={"search": "doe"})

    print(response.json())
    assert response.status_code == 200
