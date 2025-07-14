import pytest
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta

from main import app
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User, BillingPlan, UserSubscription

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

@pytest.fixture
def mock_user_sub_service():
    with patch("api.v1.services.user_subscription.user_subscription_service", autospec=True) as user_sub_service_mock:
        yield user_sub_service_mock

# Test User
@pytest.fixture
def test_user():
    return User(
        id=str(uuid7().hex),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
        is_superadmin=True
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
def test_user_subscription(test_user, test_billing_plan):
    user_sub = UserSubscription(
        id=str(uuid7().hex),
        user_id=test_user.id,
        start_date=datetime.now(),
        billing_plan_id=test_billing_plan.id,
        created_at=datetime.now(tz=timezone.utc),
        end_date=datetime.now() + timedelta(days=30),
    )
    user_sub.billing_plan = test_billing_plan
    user_sub.user = test_user
    return user_sub


@pytest.fixture
def access_token_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)

@pytest.fixture
def random_access_tokenr():
    return user_service.create_access_token(user_id='hshsdgdgdgdgdgdg')

def make_request(token):
    return client.get(
        "/api/v1/user-subscriptions", 
        headers={"Authorization": f"Bearer {token}"}
    )


# Test for successful retrieve of user subscriptions
@patch("api.v1.services.user_subscription.user_subscription_service.dictize_user_subscriptions_and_pagination")
def test_get_user_subscriptions_successful(
    mock_dictize_user_subscriptions_and_pagination,
    mock_db_session,
    test_user,
    access_token_user,
    test_billing_plan,
    test_user_subscription,
):
    # Mock the query for getting user
    mock_db_session.query().filter().first.return_value = test_user

    # TEST A SINGLE USER SUBSCRIPTION FOR 1-PAGE RESULT #

    # Mock the query for subscriptions
    mock_db_session.query().all.return_value = [test_user_subscription]

    # Make request
    response = make_request(access_token_user)
    resp_d = response.json()

    print(resp_d)
    assert response.status_code == 200
    assert resp_d['success'] is True
    assert resp_d['message'] == "User subscriptions fetched successfully"

# Test for un-authenticated request
def test_for_unauthenticated_requests(
    mock_db_session,
    test_user,
    # test_user_subscription,
    access_token_user
):
    # Mock the query for getting user
    mock_db_session.query().filter().first.return_value = test_user

    # WRONG AUTH TOKEN
    response = make_request(random_access_tokenr)
    assert response.status_code == 401
    assert response.json()['message'] == "Could not validate credentials"

    # NO AUTH TOKEN
    response = client.get("/api/v1/user-subscriptions")
    assert response.status_code == 401
    assert response.json()['message'] == "Not authenticated"

    # NON-SUPERADMIN
    test_user.is_superadmin = False
    resp = make_request(access_token_user)
    assert resp.status_code == 403
    assert resp.json()[
        "message"] == "You do not have permission to access this resource"


# Test for no user subscription 
def test_for_user_subscriptions_not_found(
    mock_db_session,
    test_user,
    access_token_user
):
    # Mock the query for getting user
    mock_db_session.query().filter().first.return_value = test_user

    mock_db_session.query().all.return_value = []

    # Make request
    response = make_request(access_token_user)
    assert response.status_code == 200
    resp_d = response.json()
    assert resp_d['success'] is True
    assert resp_d['message'] == "User subscriptions fetched successfully"
    assert resp_d['data']['user_subscriptions'] == []

    pagination = resp_d['data']['pagination']
    assert pagination['pages'] == 0
    assert pagination['limit'] == 10
    assert pagination['offset'] == 0
    assert pagination['total_items'] == 0
