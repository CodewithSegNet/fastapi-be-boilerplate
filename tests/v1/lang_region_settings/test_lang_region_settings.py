import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from uuid_extensions import uuid7
import json
import os
import tempfile
from main import app
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.services.lang_region_settings import region_service
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.v1.schemas.lang_region_settings import RegionCreate, RegionUpdate
from datetime import datetime, timezone
from faker import Faker


fake = Faker()

def mock_get_current_user():
    return User(
        id=str(uuid7().hex),
        email="user103@example.com",
        password="hashed_password",
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
    
    


def test_update_region(client, db_session_mock):
    '''Test for updating a region successfully'''
    
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()

    
    region_id = str(uuid7().hex)
    update_data = {"region": "Updated Region", "timezone": "UTC+1", "language": "French"}
    mock_region = {**update_data, "id": region_id, "user_id": "test_user_id"}
    
    with patch("api.v1.services.lang_region_settings.region_service.create_or_update", return_value={"data": mock_region}) as mock_update:
        response = client.put(
            "api/v1/regions",
            json=update_data,
            headers={'Authorization': 'Bearer token'}
        )
        
        assert response.status_code == 200
        assert response.json() == {
            "status_code": 200,
            "success": True,
            "message": "Region created or updated successfully",
            "data": mock_region
        }

def test_get_region_by_user(client, db_session_mock):
    '''Test for fetching a specific region by user ID successfully'''
    
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()

    
    mock_region = {
        "region": "Test Region", 
        "timezone": "UTC", 
        "language": "English"
    }
    
    with patch("api.v1.services.lang_region_settings.region_service.fetch", return_value={"data": mock_region}) as mock_fetch:
        response = client.get(
            "api/v1/regions",
            headers={'Authorization': 'Bearer token'}
        )
        
        assert response.status_code == 200
        assert response.json() == {
            "status_code": 200,
            "success": True,
            "message": "Region retrieved successfully",
            "data": mock_region
        }