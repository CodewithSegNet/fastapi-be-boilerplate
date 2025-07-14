from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.contact_us import ContactUs
from api.v1.models.help_topics import HelpTopics
from main import app



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


def mock_post_help_topic():
    return HelpTopics(
        id=str(uuid7().hex), 
        title="How to Generate Videos from Images using Convey",
        description="Discover how to create stunning videos from your images with Convey's Image-to-Video Generator.",
    )


@patch("api.v1.services.help_topics.HelpTopicsService.create")
def test_get_help_topics(mock_create, db_session_mock, client):
    """Tests the POST /api/v1/help-topics endpoint to ensure successful retrieval of Help topics"""

    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    db_session_mock.refresh.return_value = None

    mock_create.return_value = mock_post_help_topic()

    response = client.get('/api/v1/help-topics')

    assert response.status_code == 200
