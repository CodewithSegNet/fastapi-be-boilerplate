import pytest
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User, Payment, BillingPlan

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

@pytest.fixture
def mock_user_service():
    with patch("api.v1.services.user.user_service", autospec=True) as user_service_mock:
        yield user_service_mock

# Test User
@pytest.fixture
def test_user():
    return User(
        id=str(uuid7().hex),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True
    )


@pytest.fixture
def test_billing_plan():
    return BillingPlan(
        id=str(uuid7().hex),
        plan_name="plan one",
        price=5000,
        currency="NGN",
        plan_interval="monthly",
        features=["string", "string"],
        created_at=datetime.now(tz=timezone.utc)
    )


@pytest.fixture
def access_token_test_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)

@pytest.fixture
def random_access_token():
    return user_service.create_access_token(user_id="dhdhdhdgsgsgsffs")

def make_request(billing_plan):
    return client.get(
        f"/api/v1/billing-plans/{billing_plan.id}"
    )


# Test for successful retrieve of billing plan
# NO AUTHENTICATION
def test_get_billing_plan_successful(
    mock_db_session,
    test_user,
    test_billing_plan,
):
    # Mock the query for getting user
    mock_db_session.query().filter().first.return_value = test_user

    # Mock the query for billing_plan
    mock_db_session.get.return_value = test_billing_plan

    # Make request
    response = make_request(test_billing_plan)
    resp_d = response.json()

    assert response.status_code == 200
    assert resp_d['success'] is True
    assert resp_d['message'] == "Billing plan fetched successfully"

    plan = resp_d['data']
    assert plan['id'] == test_billing_plan.id
    assert plan['currency'] == test_billing_plan.currency
    assert plan['features'] == test_billing_plan.features
    assert float(plan['price']) == test_billing_plan.price
    assert plan['plan_name'] == test_billing_plan.plan_name
    assert datetime.fromisoformat(plan['created_at']) == test_billing_plan.created_at


# Test that authenticated requests also goes through
def test_for_authenticated_request_goes_through(
    mock_db_session,
    test_user,
    test_billing_plan,
    access_token_test_user
):
    # Mock the query for getting user
    mock_db_session.query().filter().first.return_value = test_user

    headers = {"Authorization": f"Bearer {access_token_test_user}"}
    response = client.get(
        f"/api/v1/billing-plans/{test_billing_plan.id}", headers=headers)

    # Mock the query for billing plan
    mock_db_session.get.return_value = test_billing_plan

    # Make request
    response = make_request(test_billing_plan)

    assert response.status_code == 200
    assert response.json()['success'] is True
    assert response.json()['message'] == "Billing plan fetched successfully"


# Test for no billing plan 
def test_for_billing_plan_not_found(
    mock_db_session,
    test_user,
    test_billing_plan
):
    # Mock the query for getting user
    mock_db_session.query().filter().first.return_value = test_user

    mock_db_session.get.return_value = None

    # Make request
    response = make_request(test_billing_plan)
    print(response.json())
    assert response.status_code == 404
    assert response.json()['message'] == "BillingPlan does not exist"
    assert not response.json().get('data')
