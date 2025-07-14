from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.testimonial import Testimonial
from api.v1.services.testimonial import testimonial_service
from api.v1.services.user import user_service
from datetime import datetime, timezone
from uuid_extensions import uuid7


from main import app


def mock_testimonial():
    return Testimonial(
        id=str(uuid7().hex),
        client_name="Zxenon",
        content="Very Useful Product",
        client_position="Mentor",
        rating=4.5,
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


ENDPOINT = '/api/v1/testimonials'

class TestCodeUnderTest:
    @classmethod 
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_super_admin] = lambda: MagicMock()
        app.dependency_overrides[get_db] = mock_db_session

        
    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    def test_get_all_testimonial(self, client):
        """Test to verify response for getting all testimonials."""

        mock_data = [
            Testimonial(id=str(uuid7().hex), client_name="Zxenon", content="Very Useful Product",
                        rating=4.5, created_at=datetime.now(timezone.utc),
                        client_position="Mentor",
                        updated_at=datetime.now(timezone.utc)
                        ),
            Testimonial(id=str(uuid7().hex), client_name="Zeus", content="Doesn't strike me as useful",
                        rating=2, created_at=datetime.now(timezone.utc),
                        client_position="Mentor",
                        updated_at=datetime.now(timezone.utc)
                        ) 
        ]

        app.dependency_overrides[testimonial_service.fetch_all] = mock_data

        with patch("api.v1.services.testimonial.testimonial_service.fetch_all", return_value=mock_data):
            response = client.get(ENDPOINT)

            assert response.status_code == 200
            assert response.json()['data'][0]['content'] == mock_data[0].content
            assert response.json()['data'][1]['client_name'] == mock_data[1].client_name

    
    def test_get_all_testimonials_empty(self, client):
        """Test to verify response for getting empty list of testimonials."""

        mock_data = []

        app.dependency_overrides[testimonial_service.fetch_all] = mock_data

        with patch("api.v1.services.testimonial.testimonial_service.fetch_all", return_value=mock_data):
            response = client.get(ENDPOINT)

            assert response.status_code == 200
            assert response.json().get('data') == None
        


    def test_get_testimonial_single(self, client):
        '''Test to successfully fetch a single testimonial'''

        mock_data = mock_testimonial()

        with patch("api.v1.services.testimonial.testimonial_service.fetch",
                   return_value=mock_data) as mock_fetch:
            
            response = client.get(
                f'{ENDPOINT}/{mock_data.id}',
            )

            assert response.status_code == 200
            assert response.json()['data']['content'] == mock_data.content
            assert response.json()['data']['client_name'] == mock_data.client_name

    def test_get_testimonial_not_found(self, client):
        """Test when the testimonial ID does not exist."""

        nonexistent_id = str(uuid7().hex)
        with patch("api.v1.services.testimonial.testimonial_service.fetch", return_value=None):
            response = client.get(
                f'{ENDPOINT}/{nonexistent_id}',
            )

            # Assert that the response status code is 404 Not Found
            assert response.status_code == 404
            assert response.json()['message'] == 'Testimonial not found'