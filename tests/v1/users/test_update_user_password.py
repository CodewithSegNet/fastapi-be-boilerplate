import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from uuid_extensions import uuid7


from main import app
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models.user import User
from faker import Faker

fake = Faker()



def mock_get_current_user():
    return User(
        id=str(uuid7().hex),
        email="user103@example.com",
        password=user_service.hash_password("TestaUser@123"),
        first_name='John',
        last_name='Doe',
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
def mock_other_current_user():
    return User(
        id=str(uuid7().hex),
        email="user3@example.com",
        password="",
        first_name='John',
        last_name='Doe',
        is_active=True,
        is_superadmin=False,
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



def test_change_password_success(client, db_session_mock):
    '''Test for successfully changing the user's password'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()
    
    # Mock the password change behavior
    with patch("api.v1.services.user.user_service.change_password", return_value={"message": "Password changed successfully"}) as mock_change_password:
        response = client.put(
            "/api/v1/users/update/password",
            json={
                "old_password": "TestaUser@123",
                "new_password": "NewPass123!",
                "confirm_new_password": "NewPass123!"
            },
            headers={'Authorization': 'Bearer token'}
        )

        # Assert that the response was successful
        assert response.status_code == 200




def test_change_password_incorrect_old_password(client, db_session_mock):
    '''Test for incorrect old password when changing password'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()

    # Mock the password change behavior to simulate an incorrect old password
    with patch("api.v1.services.user.user_service.change_password", side_effect=HTTPException(status_code=400, detail="Incorrect old password")) as mock_change_password:
        response = client.put(
            "/api/v1/users/update/password",
            json={
                "old_password": "WrongOldPass123",
                "new_password": "NewPass123!",
                "confirm_new_password": "NewPass123!"
            },
            headers={'Authorization': 'Bearer token'}
        )

        # Assert that the response status code is 400
        assert response.status_code == 400
 
 

def test_change_password_invalid_new_password(client, db_session_mock):
    '''Test for invalid new password'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()

    response = client.put(
        "/api/v1/users/update/password",
        json={
            "old_password": "TestaUser@123",
            "new_password": "short",
            "confirm_new_password": "Short"
        },
        headers={'Authorization': 'Bearer token'}
    )

    # Assert that the response status code is 400
    assert response.status_code == 400



def test_change_password_unauthorized(client):
    '''Test unauthorized access when no token is provided'''

    response = client.put(
        "/api/v1/users/update/password",
        json={
            "old_password": "TestaUser@123",
            "new_password": "NewPass123!",
            "confirm_new_password": "NewPass123!"
        }
    )

    # Assert that the response status code is 401
    assert response.status_code == 401
