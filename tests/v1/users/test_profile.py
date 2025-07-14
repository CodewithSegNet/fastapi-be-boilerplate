import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from uuid_extensions import uuid7
import json
import os
from minio import Minio

import tempfile
from main import app
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.v1.models.profile import Profile
from api.v1.services.profile import profile_service
from api.utils.minio_service import minio_service
from tempfile import NamedTemporaryFile
from faker import Faker

fake = Faker()



# Mock Minio client
@pytest.fixture
def mock_minio_service():
    with patch("api.utils.minio_service.Minio") as mock_minio:
        mock_client = MagicMock()
        mock_minio.return_value = mock_client
        yield mock_client

def create_temp_file():
    # Create a temporary file to simulate an avatar upload
    with NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"Test file content")
        tmp_file_path = tmp_file.name
    return tmp_file_path


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

def mock_profile():
    return Profile(
        id=str(uuid7().hex),
        user_id=str(uuid7().hex),
        username="john_doe",
        pronouns="he/him",
        job_title="Software Engineer",
        social='{"twitter": "@username", "linkedin": "linkedin.com/in/username"}',
        bio="Passionate software engineer with a love for open-source projects.",
        phone_number="+1234567890",
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
    
    
def create_temp_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file.write(b"fake image content")
    temp_file.close()
    return temp_file.name
    
    

def test_get_user_profile(client, db_session_mock):
    '''Test for fetching user profile successfully'''

    # Mock the user service to return the current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()

    # Mock the profile fetching behavior
    mock_profile_instance = mock_profile()
    with patch("api.v1.services.profile.profile_service.fetch_by_user_id", return_value=mock_profile_instance) as mock_fetch:
        response = client.get(
            "/api/v1/profile/me",
            headers={'Authorization': 'Bearer token'}
        )

        # Assert that the response was successful
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['data'] 
        assert response_data['status_code'] == 200   
   
    

def test_get_profile_not_found(client, db_session_mock):
    '''Test for fetching profile when the user does not exist'''
    
    # Mock the user service to return a current user
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()
    
    # Mock profile fetch behavior to return None, simulating a non-existing profile
    with patch("api.v1.services.profile.profile_service.fetch_by_user_id", side_effect=HTTPException(status_code=404, detail="Profile not found")) as mock_fetch:
        response = client.get(
            "/api/v1/profile/me",
            headers={'Authorization': 'Bearer token'}
        )

        # Assert that the response status code is 404
        assert response.status_code == 404
        response_data = response.json()
        assert response_data['status_code'] == 404  
        


# Test for unauthorized access
def test_update_profile_unauthorized(client):
    '''Test unauthorized access when no token is provided'''
    response = client.put(
        "/api/v1/profile",  
        json={}
    )
    response_data = response.json()
    assert response.status_code == 401
    assert response_data['status_code'] == 401