# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy.orm import Session
# from unittest.mock import MagicMock, patch

# from main import app  # Assuming your FastAPI instance is in the main.py file
# from api.v1.services.presets import preset_service

# client = TestClient(app)

# @pytest.fixture
# def mock_db():
#     """Fixture for mocking the database session."""
#     return MagicMock(spec=Session)

# @pytest.fixture
# def mock_background_tasks():
#     """Fixture for mocking BackgroundTasks."""
#     return MagicMock()

# @patch("api.db.database.get_db", return_value=MagicMock(spec=Session))
# def test_get_all_avatars(mock_get_db):
#     response = client.get("/api/v1/presets/avatars")
#     assert response.status_code == 200

# @patch("api.v1.services.presets.preset_service.load_avatars_in_db")
# @patch("api.db.database.get_db", return_value=MagicMock(spec=Session))
# def test_load_all_avatars(mock_get_db, mock_load_avatars):
#     response = client.get("/api/v1/presets/load-avatars")
#     assert response.status_code == 200

# @patch("api.v1.services.presets.preset_service.delete_all_avatars")
# @patch("api.db.database.get_db", return_value=MagicMock(spec=Session))
# def test_delete_all_avatars(mock_get_db, mock_delete_avatars):
#     response = client.delete("/api/v1/presets/avatars")
#     assert response.status_code == 204

# @patch("api.db.database.get_db", return_value=MagicMock(spec=Session))
# def test_get_all_audio(mock_get_db):
#     response = client.get("/api/v1/presets/audio")
#     assert response.status_code == 200

# @patch("api.v1.services.presets.preset_service.load_music_in_db")
# @patch("api.db.database.get_db", return_value=MagicMock(spec=Session))
# def test_load_all_audio(mock_get_db, mock_load_audio):
#     response = client.get("/api/v1/presets/load-audio")
#     assert response.status_code == 200

# @patch("api.v1.services.presets.preset_service.delete_all_avatars")
# @patch("api.db.database.get_db", return_value=MagicMock(spec=Session))
# def test_delete_all_avatars(mock_get_db, mock_delete_avatars):
#     response = client.delete("/api/v1/presets/avatars")
#     assert response.status_code == 204

# @patch("api.db.database.get_db", return_value=MagicMock(spec=Session))
# def test_get_all_audio(mock_get_db):
#     response = client.get("/api/v1/presets/audio")
#     assert response.status_code == 200

# @patch("api.v1.services.presets.preset_service.load_music_in_db")
# @patch("api.db.database.get_db", return_value=MagicMock(spec=Session))
# def test_load_all_audio(mock_get_db, mock_load_audio):
#     response = client.get("/api/v1/presets/load-audio")
#     assert response.status_code == 200

# @patch("api.v1.services.presets.preset_service.delete_all_music")
# @patch("api.db.database.get_db", return_value=MagicMock(spec=Session))
# def test_delete_all_audio(mock_get_db, mock_delete_music):
#     response = client.delete("/api/v1/presets/audio")
#     assert response.status_code == 204

# @patch("api.v1.services.presets.preset_service.generate_avatars")
# @patch("api.db.database.get_db", return_value=MagicMock(spec=Session))
# def test_generate_new_avatars(mock_get_db, mock_generate_avatars):
#     response = client.get("/api/v1/presets/avatars/generate")
#     assert response.status_code == 200
