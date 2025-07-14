from collections import namedtuple
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from api.v1.routes.tools.talking_avatar import video_router

client = TestClient(app)

@pytest.mark.asyncio
@patch('api.v1.services.job.tifi_job_service.create')
async def test_script_to_video_success_validation_error(
    mock_create
):
    # Arrange
    TifiJob = namedtuple('TifiJob', ['id'])
    mock_create.return_value = TifiJob(id="test_job_id")

    # Act
    response = client.post(
        "/api/v1/tools/video/text-to-video/generate-video",
        json={
            "script": "test script",
        }
    )

    # Assert
    assert response.status_code == 422
    

# @pytest.mark.asyncio
# @patch('api.v1.services.job.tifi_job_service.create')
# @patch('api.v1.services.presets.preset_service.fetch_music_by_id')
# async def test_script_to_video_success(
#     # mock_create_project_with_job,
#     # mock_apply_async,
#     mock_create,
#     mock_music_by_id
# ):
#     # Arrange
#     TifiJob = namedtuple('TifiJob', ['id'])
#     BackgroundMusic = namedtuple('BackgroundMusic', ['file_path'])

#     mock_create.return_value = TifiJob(id="test_job_id")

#     # Mock the audio object with a file_path attribute
#     mock_music_by_id.return_value = BackgroundMusic(file_path="path/to/audio/file")

#     # Act
#     response = client.post(
#         "/api/v1/tools/video/text-to-video/generate-video",
#         json={
#             "script": "Test script to test video",
#             # "audio_id": "audio-id",
#             "aspect_ratio": "horizontal",
#             "voice_over": "woman",
#             "scenes": [
#                 "A man jogging with a red shirt and white shoes", 
#                 "1. In a bustling office, a group of programmers sit at their computers", 
#                 "2. A young child sits in front of a computer, eagerly typing "
#             ]
#         }
#     )

    # Assert
    # assert response.status_code == 202 or response.status_code == 403 


@patch("api.v1.services.tools.script_to_video.ttv_service.recompose_script")
def test_recompose_script(mock_recompose_script):
    # Arrange
    mock_script = "This is an example script."
    mock_recomposed_script = "This is the recomposed version of the example script."
    mock_recompose_script.return_value = mock_recomposed_script
    
    # Act
    response = client.post(
        "/api/v1/tools/video/text-to-video/recompose-script",
        json={"script": mock_script}
    )
    
    # Assert
    assert response.status_code == 200
