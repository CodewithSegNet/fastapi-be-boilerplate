from io import StringIO
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from api.v1.services.user import user_service
from api.v1.services.job import tifi_job_service
from api.v1.models import User
from main import app

client = TestClient(app)
endpoint = "/api/v1/jobs/export"


def mock_csv_content():
    sample_csv_content = StringIO()
    sample_csv_content.write(
        "ID, Firstname, Lastname, Email, Title, Description, Project Type, Duration, Size, Status\n"
    )
    sample_csv_content.write(
        "123, Test, User, test@example.com, summarized-pdf, A summarized pdf, pdf, ,10KB, completed\n"
    )
    sample_csv_content.seek(0)

    return sample_csv_content


def test_export_success(
    db_session_mock,
    test_admin_user,
    access_token,
):
    mock_csv = mock_csv_content()

    with patch(
        "api.v1.services.job.tifi_job_service.export_jobs_as_csv",
        return_value=mock_csv,
    ) as mock_export:
        response = client.get(
            endpoint, headers={"Authorization": f"Bearer {access_token}"}
        )

        # Assert the response status code
        assert response.status_code == 200