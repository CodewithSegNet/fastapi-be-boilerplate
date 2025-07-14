#!/usr/bin/env/python3

"""Test for youtube_summarizer tool"""


from collections import namedtuple
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from api.v1.routes.tools.youtube_video_summarizer import video_summary
from api.db.database import get_db
from main import app
from api.v1.models.project import ProjectToolsEnum
from sqlalchemy.orm import Session
from api.utils.tool_limiter import ACCESS_LIMIT

# Create a test client
client = TestClient(app)

# Mock the database session for dependency injection


@pytest.fixture
def mock_db():
    yield AsyncMock()


def mock_db_session():
    return MagicMock()


@pytest.fixture
# def mock_create_project_with_job():
def mock_create():
    with patch("api.v1.services.job.tifi_job_service.create") as mock:

        TifiJob = namedtuple('TifiJob', ['id'])
        mock.return_value = TifiJob(id="test_job_id")
        yield mock


@pytest.fixture
def override_get_db(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides = {}


# Test the endpoint
def test_youtube_summarizer_single(
    mock_create,
    override_get_db,
):
    # Prepare test files
    data = {
        "link": "https://www.youtube.com/watch?v=testvideo",
        "detail_level": "short"
    }

    mocked_db = mock_db_session()

    app.dependency_overrides[get_db] = lambda: mocked_db

    # Send a POST request to the summarize_batch endpoint
    response = client.post(
        "/api/v1/tools/summary/summarize-youtube-video",
        json=data,
    )

    # Assertions
    assert response.status_code == 202


# def test_youtube_summarize_job_limiting(
#     mock_create,
#     override_get_db,
# ):
#     # Prepare test files
#     link = {"link": "https://www.youtube.com/watch?v=testvideo"}

#     mocked_db = mock_db_session()

#     mock_filter = mock_db_session()
#     mock_first = mock_db_session()
#     mock_data = mock_db_session()

#     mocked_db.query.return_value = mock_filter
#     mock_filter.filter_by.return_value = mock_first
#     mock_first.first.return_value = mock_data
#     mock_data.tools_accessed = []

#     app.dependency_overrides[get_db] = lambda: mocked_db

#     for i in range(ACCESS_LIMIT):
#         # Send a POST request to the summarize multiple times to test limiter
#         response = client.post(
#             "/api/v1/tools/summary/summarize-youtube-video",
#             json=link,
#         )

#         # Assertions
#         assert response.status_code == 202
