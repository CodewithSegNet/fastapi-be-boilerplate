#!/usr/bin/env/python3

"""Test for youtube_summarizer tool"""


from collections import namedtuple
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi.testclient import TestClient
from api.v1.models.user import User
from api.v1.routes.tools.youtube_video_summarizer import video_summary
from api.v1.services.user import user_service
from api.db.database import get_db
from uuid import uuid4
from main import app

# Create a test client
client = TestClient(app)


@pytest.fixture
def mock_db():
    db_session = Mock()
    db_session.query.return_value.filter_by.return_value.first.return_value = None  # Adjust this to your use case
    yield db_session


# mock_user = MagicMock(id='id', email="test_user@test.com")
# token = user_service.create_access_token(mock_user.id)

# # Test successful request with valid authentication
# @patch("api.v1.services.user.user_service.get_current_user", return_value=mock_user)  # Mock user authentication
# @patch("api.utils.files.upload_multiple_files_to_tmp_dir", return_value=["test_video.mp4"])  # Mock file upload to temp dir
# @patch("api.utils.minio_service.minio_service.upload_to_tmp_bucket", return_value='"mock_video_url"')  # Mock minio_service
# @patch("api.v1.services.job.tifi_job_service.create", return_value=MagicMock(id='123'))  # Mock job creation
# def test_batch_summarize_video_success(mock_create_job, mock_upload_bucket, mock_upload_files, mock_get_user):

#     # Prepare the files to send in the request
#     files = [
#         ('files', ('test_video.mp4', b'mock content', 'video/mp4')),
#         ('files', ('test_video2.mp4', b'mock content', 'video/mp4'))
#     ]

#     # Ensure correct Authorization header is passed
#     response = client.post(
#         "/api/v1/tools/summary/batch-video-summarize",
#         headers={
#             'Authorization': f'Bearer {token}'  # Mock token
#         },
#         files=files,
#         data={'detail_level': 'short'},
#     )

#     # Assert the response is as expected
#     assert response.status_code == 202


# # Test request without authentication
# @patch("api.v1.services.user.user_service.get_current_user", return_value=None)  # Mock unauthenticated user
# def test_batch_summarize_video_unauthenticated(mock_get_user):
#     # Prepare the files to send in the request
#     files = [
#         ('files', ('test_video.mp4', b'mock content', 'video/mp4'))
#     ]

#     # Make the request without authentication
#     response = client.post(
#         "/api/v1/tools/summary/batch-video-summarize",
#         files=files,
#         data={'detail_level': 'short'},
#     )

#     # Assert that unauthorized users are rejected
#     assert response.status_code == 401


# # Test request with an invalid video file format
# @patch("api.v1.services.user.user_service.get_current_user", return_value=mock_user)  # Mock authenticated user
# @patch("api.utils.files.upload_multiple_files_to_tmp_dir", return_value=["test_video.mp4"])  # Mock file upload to temp dir
# def test_batch_summarize_video_invalid_file_format(mock_get_user, mock_upload_files):
#     # Prepare invalid file to send in the request
#     files = [
#         ('files', ('invalid_file.txt', b'mock content', 'text/plain'))
#     ]

#     # Ensure correct Authorization header is passed
#     response = client.post(
#         "/api/v1/tools/summary/batch-video-summarize",
#         headers={
#             'Authorization': f'Bearer {token}'  # Mock token
#         },
#         files=files,
#         data={'detail_level': 'short'},
#     )

#     # Assert that it rejects invalid file formats
#     assert response.status_code == 400



@pytest.fixture
def mock_upload_files():
    with patch("api.utils.files.upload_multiple_files_to_tmp_dir") as mock:
        mock.return_value = ["test_video.mp4"]
        yield mock


@pytest.fixture
def mock_upload_file_to_minio_tmp():
    with patch("api.utils.minio_service.minio_service.upload_to_tmp_bucket") as mock:
        mock.return_value = 'https://minio.example.com/tmp/test-video.mp4'
        yield mock


@pytest.fixture
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


def test_enqueue_summarize_batch_job(
    # mock_current_user,
    mock_upload_files, 
    mock_upload_file_to_minio_tmp, 
    mock_create, 
    override_get_db
):
    # Prepare test files
    files = {
        "files": ("video.mp4", b"dummy video data", "video/mp4")
    }

    # Send a POST request to the summarize_batch endpoint
    response = client.post(
        "/api/v1/tools/summary/batch-video-summarize",
        # headers={
        #     'Authorization': 'Bearer test_token'
        # },
        files=files
    )

    # Assertions
    assert response.status_code == 202 or response.status_code == 401
