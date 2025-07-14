from api.v1.models.newsletter import Newsletter
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock,patch
from main import app
from api.v1.models.billing_plan import BillingPlan
from api.v1.models.user import User
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone
import uuid
import time


client = TestClient(app)

# Mock the database dependency
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
    # Clean up after the test by removing the override
    app.dependency_overrides = {}


def test_user_login(db_session_mock):
    """Test for successful inactive user login."""

    # Create a mock user
    mock_user = User(
        id=str(uuid7().hex),
        email="testuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=False,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_user

    # Login with mock user details
    login = client.post("/api/v1/auth/login", json={
        "email": "testuser1@gmail.com",
        "password": "Testpassword@123"
    })
    response = login.json()
    assert response.get("status_code") == status.HTTP_200_OK

def test_rate_limiting(db_session_mock):
    db_session_mock.query(User).filter().first.return_value = None
    billing_plan =  BillingPlan(id=str(uuid7().hex),plan_name='Free', price='5.00',currency='dollars', features=['testfeature1', 'testfeature2'], access_limit=15)
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None
    
    unique_email = f"rate.limit.{uuid.uuid4().hex}@gmail.com"
    user = {
        "password": "ValidP@ssw0rd!",
        "first_name": "Rate",
        "last_name": "Limit",
        "email": unique_email
    }

    with patch('api.v1.services.billing_plan.billing_plan_service.subscribe_user_to_free_plan', return_value = billing_plan) as mock_service:

         response = client.post("/api/v1/auth/register", json=user)
         assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
    
         time.sleep(5)  # Adjust this delay to see if it prevents rate limiting

         for _ in range(5):
             response = client.post("/api/v1/auth/register", json=user)
             assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"