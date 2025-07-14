from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid_extensions import uuid7
from main import app
from api.db.database import get_db
from api.v1.models.blog import Blog
from api.v1.services.user import oauth2_scheme, user_service
from api.v1.schemas.blog import BlogCreate, BlogUpdate

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_blog():
    return Blog(
        id=str(uuid7().hex),
        title="Test Blog Title",
        content="Test Blog Content",
        image_url="http://example.com/image.jpg",
        cover_image_url="http://example.com/cover.jpg",
        is_deleted=False,
        category="Tech",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_deps():
    return MagicMock(id="user_id")

@pytest.fixture
def setup_dependencies(mock_db_session):
    app.dependency_overrides[user_service.get_current_super_admin] = mock_deps
    app.dependency_overrides[get_db] = lambda: mock_db_session
    yield
    app.dependency_overrides = {}

class TestBlogEndpoints:
    @pytest.mark.usefixtures("setup_dependencies")
    def test_get_all_blogs(self, client, mock_blog):
        """Test to verify response for getting all blogs."""
        mock_blog_data = [
            mock_blog,
            Blog(
                id=str(uuid7().hex), title="Another Blog", content="Another Content",
                image_url="http://example.com/another.jpg", cover_image_url="http://example.com/another_cover.jpg",
                is_deleted=False, category="Health", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
        ]

        with patch("api.utils.pagination.paginated_response", return_value=mock_blog_data):
            response = client.get('/api/v1/blog')

            assert response.status_code == 200

    @pytest.mark.usefixtures("setup_dependencies")
    def test_get_all_blogs_empty(self, client):
        """Test to verify response for getting all blogs, even when there are none."""

        with patch("api.v1.services.blog.blog_service.fetch_all", return_value=[]):
            response = client.get('/api/v1/blog')

            assert response.status_code == 200

    @pytest.mark.usefixtures("setup_dependencies")
    def test_get_blog_single(self, client, mock_blog):
        """Test to successfully fetch a specific blog"""

        with patch("api.v1.services.blog.blog_service.fetch", return_value=mock_blog):
            response = client.get(f'/api/v1/blog/{mock_blog.id}')

            assert response.status_code == 200
 

    @pytest.mark.usefixtures("setup_dependencies")
    def test_create_blog(self, client, mock_blog):
        """Test to create a new blog."""

        mock_blog_create = BlogCreate(
            title="New Blog Title",
            content="New Blog Content",
            image_url="http://example.com/new_image.jpg",
            cover_image_url="http://example.com/new_cover.jpg",
            category="Lifestyle"
        )

        with patch("api.v1.services.blog.blog_service.create", return_value=mock_blog):
            response = client.post('/api/v1/blog', json=mock_blog_create.dict())

            assert response.status_code == 201
 

    @pytest.mark.usefixtures("setup_dependencies")
    def test_update_blog(self, client, mock_blog):
        """Test to update an existing blog."""

        mock_blog_update = BlogUpdate(
            title="Updated Blog Title",
            content="Updated Blog Content",
            image_url="http://example.com/updated_image.jpg",
            cover_image_url="http://example.com/updated_cover.jpg",
            category="Updated Category"
        )

        with patch("api.v1.services.blog.blog_service.update", return_value=mock_blog):
            response = client.put(f'/api/v1/blog/{mock_blog.id}', json=mock_blog_update.dict())

            assert response.status_code == 200