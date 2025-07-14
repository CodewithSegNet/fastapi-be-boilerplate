import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from api.v1.services.user import oauth2_scheme, user_service
from api.db.database import get_db
from api.v1.models.faq import FAQ
from main import app

def mock_faq():
    return FAQ(
        id=str(uuid7().hex),
        question="TTest question?",
        answer="TAnswer",
        category="Policies",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_deps():
    return MagicMock(id="user_id")

def mock_oauth():
    return 'access_token'

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

mocked_db = MagicMock(spec=Session)

class TestCodeUnderTest:
    @classmethod
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_super_admin] = mock_deps
        app.dependency_overrides[get_db] = lambda: mocked_db

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Successfully delete faq from the database
    def test_delete_faq_success(self, client):
        mock_freq_asked_questions = mock_faq()
        with patch("api.v1.services.faq.faq_service.delete",
                   return_value=mock_freq_asked_questions) as mock_fetch:
            
            response = client.delete(f'/api/v1/faqs/{mock_freq_asked_questions.id}')

            assert response.status_code == 204
            mock_fetch.assert_called_once_with(mocked_db, faq_id=mock_freq_asked_questions.id)

    
    # Invalid id
    def test_delete_faq_invalid_id(self, client):
        
        with patch('api.v1.services.faq.faq_service.fetch', return_value=None):
            response = client.delete('/api/v1/faqs/2')
            assert response.status_code == 404
            assert response.json()['message'] == "FAQ not found"

  # Handling forbidden request
    def test_delete_faq_forbidden(self, client):
        app.dependency_overrides = {}
        app.dependency_overrides[get_db] = lambda: mocked_db
        app.dependency_overrides[oauth2_scheme] = mock_oauth

        with patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_superadmin=False)) as cu:
            response = client.delete('/api/v1/faqs/swe')
            assert response.status_code == 403
            assert response.json()['message'] == 'You do not have permission to access this resource'