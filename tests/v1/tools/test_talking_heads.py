from collections import namedtuple
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from main import app
from api.v1.routes.tools.talking_avatar import video_router

client = TestClient(app)

# @pytest.mark.asyncio
# @patch('api.v1.routes.ai_tools.talking_avatar.upload_to_temp_dir')
# @patch('api.v1.routes.ai_tools.talking_avatar.preset_service.fetch_music_by_id')
# @patch('api.v1.services.job.tifi_job_service.create')
# # @patch('api.v1.routes.ai_tools.talking_avatar.contains_face')
# # @patch('api.v1.routes.ai_tools.talking_avatar.generate_talking_avatar_task.apply_async')
# # @patch('api.v1.routes.ai_tools.talking_avatar.job_service.create_project_with_job')
# async def test_talking_head_image_upload(
#     # mock_create_project_with_job, 
#     # mock_apply_async, 
#     # mock_contains_face
#     mock_fetch_music_by_id, 
#     mock_upload_to_temp_dir,
#     mock_create,
# ):
#     TifiJob = namedtuple('TifiJob', ['id'])
#     Project = namedtuple('Project', ['id'])
#     BackgroundMusic = namedtuple('BackgroundMusic', ['file_path'])
    
#     # Arrange
#     mock_upload_to_temp_dir.return_value = "test_image.jpg"
#     mock_fetch_music_by_id.return_value = BackgroundMusic(file_path="test_audio.mp3")
#     mock_create.return_value = (TifiJob(id="test_job_id"), Project(id="test_project_id"))
#     # mock_fetch_music_by_id.return_value = MagicMock(file_path="test_audio.mp3")
#     # mock_apply_async.return_value.id = "test_task_id"
#     # mock_create_project_with_job.return_value.id = "test_project_id"
#     # mock_contains_face.return_value = "True"

#     # Act
#     response = client.post(
#         "/api/v1/tools/video/talking-head/image-upload",
#         data={
#             "script": "Test script",
#             "aspect_ratio": "16:9",
#             "voice_over": "male",
#             "audio_id": "123"
#         },
#         files={"file": ("test.jpg", b"filecontent", "image/jpeg")}
#     )

#     # Assert
#     assert response.status_code == 202 or response.status_code == 403

# @pytest.mark.asyncio
# @patch('api.v1.routes.ai_tools.talking_avatar.preset_service.fetch_music_by_id')
# @patch('api.v1.routes.ai_tools.talking_avatar.preset_service.fetch_avatar_by_id')
# @patch('api.v1.services.job.tifi_job_service.create')
# # @patch('api.v1.routes.ai_tools.talking_avatar.contains_face')
# # @patch('api.v1.routes.ai_tools.talking_avatar.generate_talking_avatar_task.apply_async')
# # @patch('api.v1.routes.ai_tools.talking_avatar.job_service.create_project_with_job')
# # @patch('api.v1.services.usage.usage_store_service.fetch_tool_access_by_usage_store_and_name')
# # @patch('api.v1.services.usage.usage_store_service.fetch_by_id')
# async def test_talking_head_avatar_selection(
#     # mock_create_project_with_job,
#     # mock_apply_async,
#     mock_create,
#     mock_fetch_music_by_id,
#     mock_fetch_avatar_by_id,
#     # mock_fetch_tool_access_by_usage_store_and_name,
#     # mock_fetch_by_id
# ):
#     # Arrange
#     mock_fetch_avatar_by_id.return_value = MagicMock(file_path="test_avatar.jpg")
#     mock_fetch_music_by_id.return_value = MagicMock(file_path="test_audio.mp3")
#     # mock_apply_async.return_value.id = "test_task_id"
#     # mock_create_project_with_job.return_value.id = "test_project_id"
#     # mock_fetch_tool_access_by_usage_store_and_name.return_value = MagicMock(
#     #     tool_name="Talking Avatar",
#     #     access_count=0,
#     #     last_accessed=datetime.utcnow()
#     # )
#     # mock_fetch_by_id.return_value = MagicMock(
#     #     tool_access_count=0,
#     #     last_accessed=datetime.utcnow()
#     # )

#     TifiJob = namedtuple('TifiJob', ['id'])
#     Project = namedtuple('Project', ['id'])

#     mock_create.return_value = (TifiJob(id="test_job_id"), Project(id="test_project_id"))

#     # Act
#     response = client.post(
#         "/api/v1/tools/video/talking-head/avatar-selection",
#         json={
#             "avatar_id": "avatar_123",
#             "audio_id": "audio_123",
#             "script": "Test script",
#             "aspect_ratio": "vertical",
#             "voice_over": "man"
#         }
#     )

#     # Assert
#     assert response.status_code == 202 or response.status_code == 403
