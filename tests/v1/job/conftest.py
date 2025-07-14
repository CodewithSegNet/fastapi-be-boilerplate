import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from api.db.database import get_db

# client = TestClient(app)
# endpoint = "/api/v1/jobs/activity"


@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session


# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}


@pytest.fixture
def test_admin_user():
    return User(id=str(uuid7().hex))


@pytest.fixture
def access_token(test_admin_user):
    return user_service.create_access_token(test_admin_user.id)


@pytest.fixture
def mock_paginated_response():
    with patch(
        "api.v1.services.job.job_service.fetch_job_activity"
    ) as fetch_all_summarized_videos:
        response = {
            "status_code": 200,
            "success": True,
            "message": "Successfully fetched items",
            "data": {
                "pages": 1,
                "total": 2,
                "skip": 0,
                "limit": 30,
                "items": [
                    {
                        "user_id": "066bcc17-063d-74ca-8000-61f211cfb3bb",
                        "project_id": "8031a9e4-7414-40ab-b993-8a76ae9bcc38",
                        "result": None,
                        "created_at": "2024-08-14T15:45:23.907752+01:00",
                        "job_id": "123AB",
                        "status": "COMPLETED",
                        "id": "0836dcc1-9499-446a-85aa-1e24a9d8053f",
                        "updated_at": "2024-08-14T15:45:23.907752+01:00",
                        "user": {
                            "id": "066bcc17-063d-74ca-8000-61f211cfb3bb",
                            "first_name": "Test",
                            "last_name": "User",
                        },
                        "project": {
                            "is_active": False,
                            "id": "8031a9e4-7414-40ab-b993-8a76ae9bcc38",
                            "updated_at": "2024-08-14T15:42:15.896913+01:00",
                            "user_id": "066bcc17-063d-74ca-8000-61f211cfb3bb",
                            "project_type": "video",
                            "archived_at": None,
                            "created_at": "2024-08-14T15:42:15.896913+01:00",
                        },
                    },
                    {
                        "user_id": "066bcc17-063d-74ca-8000-61f211cfb3bb",
                        "project_id": "8031a9e4-7414-40ab-b993-8a76ae9bcc38",
                        "result": None,
                        "created_at": "2024-08-14T15:45:58.542153+01:00",
                        "job_id": "123AB",
                        "status": "FAILED",
                        "id": "3f89c1ff-a87b-4708-a9c7-af1ce995a111",
                        "updated_at": "2024-08-14T15:45:58.542153+01:00",
                        "user": {
                            "id": "066bcc17-063d-74ca-8000-61f211cfb3bb",
                            "first_name": "Test",
                            "last_name": "User",
                        },
                        "project": {
                            "is_active": False,
                            "id": "8031a9e4-7414-40ab-b993-8a76ae9bcc38",
                            "updated_at": "2024-08-14T15:42:15.896913+01:00",
                            "user_id": "066bcc17-063d-74ca-8000-61f211cfb3bb",
                            "project_type": "video",
                            "archived_at": None,
                            "created_at": "2024-08-14T15:42:15.896913+01:00",
                        },
                    },
                ],
            },
        }

        fetch_all_summarized_videos.return_value = response
        yield fetch_all_summarized_videos


@pytest.fixture
def mock_get_job_statistics():
    with patch(
        "api.v1.services.job.job_service.get_job_statistics"
    ) as get_job_statistics:
        response = {
            "status_code": 200,
            "success": True,
            "message": "Job statistics retrieved successfully",
            "data": {
                "total_tasks": 2,
                "failed_tasks": 1,
                "in_progress_tasks": 0,
                "pending_tasks": 0,
                "completed_tasks": 1,
            },
        }

        get_job_statistics.return_value = response
        yield get_job_statistics


@pytest.fixture
def mock_job_activity():
    with patch("api.v1.services.job.job_service.stream_job_activity") as mock:
        response = 'data: {"job_id": "123-xxx", "status": "PENDING"}'

        mock.return_value = response
        yield mock


@pytest.fixture
def mock_job_statistics():
    with patch("api.v1.services.job.job_service.stream_job_statistics") as mock:
        response = 'data: {"total_tasks": 10, "failed_tasks": 0, "in_progress_tasks": 0, "pending_tasks": 8, "completed_tasks": 1,"created_in_last_hour": 1, "active_in_last_hour": 0,"pending_in_last_hour": 0,"completed_in_last_hour": 1}'

        mock.return_value = response
        yield mock
