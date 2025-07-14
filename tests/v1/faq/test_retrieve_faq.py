from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.faq import FAQ
from api.v1.services.faq import faq_service
from api.v1.services.user import user_service
from datetime import datetime, timezone
from uuid_extensions import uuid7


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


def mock_db_session():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client():
    client = TestClient(app)
    return client

mock_db_sess_inst = mock_db_session()

class TestCodeUnderTest:
    @classmethod 
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_super_admin] = lambda: MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db_sess_inst

        
    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_get_all_faqs(self, client):
        """Test to verify response for getting all FAQs."""

        mock_faq_data = [
            FAQ(id=str(uuid7().hex), question="TTest question?", answer="TAnswer",
                category="Policies", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
            FAQ(id=str(uuid7().hex), question="TTest question?", answer="TAnswer",
                category="Policies", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        ]

        app.dependency_overrides[faq_service.fetch_all] = mock_faq_data

        with patch("api.v1.services.faq.faq_service.fetch_all", return_value=mock_faq_data):
            response = client.get('/api/v1/faqs')

            assert response.status_code == 200
            assert response.json()['data'][0]['question'] == mock_faq_data[0].question
            assert response.json()['data'][1]['answer'] == mock_faq_data[1].answer

    def test_get_all_faqs_empty(self, client):
        """Test to verify response for getting all FAQs, even when there are
        none."""

        mock_faq_data = []

        app.dependency_overrides[faq_service.fetch_all] = mock_faq_data

        with patch("api.v1.services.faq.faq_service.fetch_all", return_value=mock_faq_data):
            response = client.get('/api/v1/faqs')

            assert response.status_code == 200
            assert response.json().get('data') == None
        


    def test_get_faq_single(self, client):
        '''Test to successfully fetch a new faq'''

        mock_freq_asked_questions = mock_faq()

        with patch("api.v1.services.faq.faq_service.fetch",
                   return_value=mock_freq_asked_questions) as mock_fetch:
            
            response = client.get(
                f'/api/v1/faqs/{mock_freq_asked_questions.id}',
            )

            assert response.status_code == 200
            assert response.json()['data']['question'] == mock_freq_asked_questions.question
            assert response.json()['data']['answer'] == mock_freq_asked_questions.answer

    def test_get_faq_not_found(self, client):
        """Test when the FAQ ID does not exist."""

        nonexistent_id = str(uuid7().hex)

        mock_query = MagicMock()
        mock_filter = MagicMock()

        mock_db_sess_inst.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_filter
        mock_filter.first.return_value = None
        
        response = client.get(
                f'/api/v1/faqs/{nonexistent_id}',
            )

            # Assert that the response status code is 404 Not Found
        assert response.status_code == 404
        assert response.json()['message'] == 'FAQ not found'