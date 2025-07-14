from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import oauth2_scheme, user_service
from api.v1.models.testimonial import Testimonial
from main import app

def mock_testimonial():
    return Testimonial(
        id=str(uuid7().hex),
        client_name="Zxenon",
        content="Very Useful Product",
        rating=4.5,
        client_position="Mentor",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )



def mock_db_session():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client():
    client = TestClient(app)
    yield client


test_patch_body = {
    "content": "Perfecto!",
    }

ENDPOINT = '/api/v1/testimonials'

class TestCodeUnderTest:
    @classmethod 
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_super_admin] = lambda: MagicMock()
        app.dependency_overrides[get_db] = mock_db_session

        
    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_patch_testimonial_success(self, client):
        '''Test to successfully update a testimonial'''

        # Mock the user service to return the current user
        app.dependency_overrides[user_service.get_current_super_admin] = lambda: MagicMock()

        mock_data = mock_testimonial()

        with patch("api.v1.services.testimonial.testimonial_service.fetch", return_value=mock_data):
            response = client.patch(
                f'{ENDPOINT}/{mock_data.id}',
                json=test_patch_body
            )

        assert response.status_code == 200
        assert response.json()['data']['content'] == test_patch_body['content']
        assert response.json()['data']['client_name'] == mock_data.client_name

    def test_patch_testimonial_empty_fields(self, client):
        '''Test for empty fields when updating an testimonial'''

        # Mock the user service to return the current user
        app.dependency_overrides[user_service.get_current_super_admin] = lambda: MagicMock()

        mock_data = mock_testimonial()

        with patch("api.v1.services.testimonial.testimonial_service.fetch", return_value=mock_data):
            response = client.patch(
                f'{ENDPOINT}/{mock_data.id}',
                json={}
            )

            assert response.status_code == 200
            assert response.json()['data']['content'] == mock_data.content
            assert response.json()['data']['rating'] == mock_data.rating


    def test_patch_testimonial_forbidden(self, client):
        """Test unauthourized user

        Args:
            client: TestClient object
            db_session_mock (MagicMock): 
        """
        app.dependency_overrides = {}
        app.dependency_overrides[get_db] = mock_db_session
        app.dependency_overrides[oauth2_scheme] = lambda: 'access_token'

        with patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_superadmin=False)) as cu:
            response = client.patch(
                f'{ENDPOINT}/23', json={}
                )

        assert response.status_code == 403
        assert response.json()['message'] == 'You do not have permission to access this resource'