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
def mock_user_service():
    with patch("api.v1.services.user.user_service", autospec=True) as user_service_mock:
        yield user_service_mock

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
        is_active=True
    )

# Super Admin
@pytest.fixture
def super_admin():
    return User(
        id=str(uuid7().hex),
        email="superadmin@gmail.com",
        password="hashedpassword",
        first_name="super",
        last_name="admin",
        is_active=True,
        is_superadmin=True
    )

# Other User
@pytest.fixture
def other_user():
    return User(
        id=str(uuid7().hex),
        email="otheruser@gmail.com",
        password="hashedpassword",
        first_name="other",
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


@pytest.fixture()
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
def access_token_test_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)

@pytest.fixture
def access_token_super_admin(super_admin):
    return user_service.create_access_token(user_id=super_admin.id)

@pytest.fixture
def random_access_token(other_user):
    return user_service.create_access_token(user_id=other_user.id)

def make_request(token, user_sub):
    return client.get(
        f"/api/v1/user-subscriptions/{user_sub.id}", 
        headers={"Authorization": f"Bearer {token}"}
    )


# Test for successful retrieve of user_subscription
@patch("api.v1.services.user_subscription.user_subscription_service.dynamic_user_subscription_dict")
def test_get_user_subscription_successful(
    mock_dynamic_user_subscription_dict,
    mock_db_session,
    test_user,
    super_admin,
    test_user_subscription,
    access_token_test_user,
    access_token_super_admin
):
    # Mock the query for getting user
    mock_db_session.query().filter().first.side_effects = [test_user, super_admin]

    # Mock the query for user_subscription
    mock_db_session.get.return_value = test_user_subscription

    # Make request
    response = make_request(access_token_test_user, test_user_subscription)
    resp_d = response.json()

    # FOR USER ONWER
    assert response.status_code == 200
    assert resp_d['success'] is True
    assert resp_d['message'] == "User subscription fetched successfully"
    
    # FOR SUPER ADMIN
    response = make_request(access_token_super_admin, test_user_subscription)
    resp_d = response.json()
    assert response.status_code == 200
    assert resp_d['success'] is True
    assert resp_d['message'] == "User subscription fetched successfully"


# Test for unauthenticated/unauthorized request
def test_for_unauthenticated_unauthorized_request(
    mock_db_session,
    test_user,
    other_user,
    test_user_subscription,
    random_access_token
):
    # Mock the query for getting user
    mock_db_session.query().filter().first.return_value = test_user

    # INVALID AUTH TOKEN
    response = make_request("invalid-access-token", test_user_subscription)
    print(response.json())
    assert response.status_code == 401
    assert response.json()['message'] == "Could not validate credentials"

    # NO AUTH TOKEN
    response = client.get(f"/api/v1/payments/{test_user_subscription.id}")
    assert response.status_code == 401
    assert response.json()['message'] == "Not authenticated"

    # NON-SUPERADMIN / NON-OWNER
    # --remove the superadmin privilege from superadmin-- #
    mock_db_session.query().filter().first.return_value = other_user
    resp = make_request(random_access_token, test_user_subscription)
    assert resp.status_code == 401
    assert resp.json()[
        "message"] == "You do not have permission to access this resource"


# Test for no payment 
def test_for_payment_not_found(
    mock_db_session,
    test_user,
    test_user_subscription,
    access_token_test_user
):
    # Mock the query for getting user
    mock_db_session.query().filter().first.return_value = test_user

    mock_db_session.get.return_value = None

    # Make request
    response = make_request(access_token_test_user, test_user_subscription)
    print(response.json())
    assert response.status_code == 404
    assert response.json()['message'] == "UserSubscription does not exist"
    assert not response.json().get('data')
