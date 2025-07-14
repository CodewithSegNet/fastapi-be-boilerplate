# import pytest
# from fastapi.testclient import TestClient
# from unittest.mock import patch
# from main import app
# from io import BytesIO 


# client = TestClient(app)

# @pytest.fixture
# def mock_celery_task():
#     with patch("api.core.dependencies.celery.tasks.audio_tasks.generate_audio_summary_task.delay") as mock_task:
#         yield mock_task

# def create_mock_file(content, filename):
#     file = BytesIO(content)
#     file.name = filename
#     return file
    
# def test_summarize_audio_no_file_uploaded(mock_celery_task):
#     # Simulate no file uploaded
#     response = client.post(
#         "/api/v1/summary/summarize-audio",
#         data={"target_lang": "es"}
#     )
    
#     assert response.status_code == 404  # Unprocessable Entity because file field is required

