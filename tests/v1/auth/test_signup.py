import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app
from api.db.database import get_db
from api.v1.models.newsletter import Newsletter
from uuid_extensions import uuid7
from api.v1.models.billing_plan import BillingPlan

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

    app.dependency_overrides = {}

def test_status_code(db_session_mock, mock_send_email):
    db_session_mock.query(Newsletter).filter().first.return_value = None
    billing_plan = BillingPlan(id=str(uuid7().hex),plan_name='Free', price='5.00',currency='dollars', features=['testfeature1', 'testfeature2'], access_limit=15)
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    user = {
        "password": "strin8Hsg263@",
        "first_name": "string",
        "last_name": "string",
        "email": "user@example.com"
    }
    with patch('api.v1.services.billing_plan.billing_plan_service.subscribe_user_to_free_plan', return_value = billing_plan) as mock_service:
         response = client.post("/api/v1/auth/register", json=user)

         assert response.status_code == 201
         # mock_send_email.assert_called_once()

def test_user_fields(db_session_mock, mock_send_email):

    db_session_mock.query(Newsletter).filter().first.return_value = None
    billing_plan = BillingPlan(id=str(uuid7().hex),plan_name='Free', price='5.00',currency='dollars', features=['testfeature1', 'testfeature2'], access_limit=15)
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    user = {
        "password": "strin8Hsg263@",
        "first_name": "sunday",
        "last_name": "mba",
        "email": "mba@gmail.com"
    }
    with patch('api.v1.services.billing_plan.billing_plan_service.subscribe_user_to_free_plan', return_value = billing_plan) as mock_service:  
         response = client.post("/api/v1/auth/register", json=user)

         assert response.status_code == 201
         assert response.json()['data']["user"]['email'] == "mba@gmail.com"
         assert response.json()['data']["user"]['first_name'] == "sunday"
         assert response.json()['data']["user"]['last_name'] == "mba"
         # mock_send_email.assert_called_once()
    