from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.db.database import get_db
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
import pytest

from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.models.billing_plan import BillingPlan


client = TestClient(app)


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
def test_user():
    return User(
        id=str(uuid7().hex),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
        is_superadmin=True,
    )


@pytest.fixture
def test_billing_plan():
    return BillingPlan(
        id=str(uuid7().hex),
        plan_name="one",
        price=5000,
        plan_interval="monthly",
        currency="NGN",
        features=["string", "string"]
    )


@pytest.fixture
def access_token_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)


@pytest.fixture
def random_access_tokenr():
    return user_service.create_access_token(user_id='hshsdgdgdgdgdgdg')


bp_update_data = {
    # Chnaged
    "price": 7000,
    "plan_name": "plan one",
    "features": ["string", "string", "string"],
}


def make_request(token, billing_plan):
    bp_update_data.update({
        # Unchanged
        "access_limit": 100,
        "currency": billing_plan.currency,
        "plan_interval": billing_plan.plan_interval
    })
    return client.patch(
        f"/api/v1/billing-plans/{billing_plan.id}", json=bp_update_data,
        headers={"Authorization": f"Bearer {token}"}
    )


# Test for successful updating
def test_update_billing_plan_successful(
    mock_db_session,
    test_user,
    test_billing_plan,
    access_token_user
):
    mock_db_session.query().filter().first.return_value = test_user

    mock_db_session.get.return_value = test_billing_plan

    resp = make_request(access_token_user, test_billing_plan)
    resp_d = resp.json()
    print(resp_d)
    assert resp.status_code == 200
    assert resp_d['success'] == True
    assert resp_d['message'] == "Billing plan updated successfully"

    bp_data = resp_d['data']
    assert bp_data['id'] == test_billing_plan.id
    assert bp_data['price'] == bp_update_data['price']
    assert bp_data['features'] == bp_update_data['features']
    assert bp_data['currency'] == test_billing_plan.currency
    assert bp_data['plan_name'] == bp_update_data['plan_name']
    assert bp_data['plan_interval'] == test_billing_plan.plan_interval


# Test for unsuccessful updating
def test_update_billing_plan_unsuccessful(
    mock_db_session,
    test_user,
    test_billing_plan,
    access_token_user,
):
    mock_db_session.query().filter().first.return_value = test_user

    # NON-SUPERADMIN
    test_user.is_superadmin = False
    resp = make_request(access_token_user, test_billing_plan)
    assert resp.status_code == 403
    assert resp.json()[
        "message"] == "You do not have permission to access this resource"

    # INVALID AUTH
    test_user.is_superadmin = True
    resp = make_request(random_access_tokenr, test_billing_plan)
    assert resp.status_code == 401
    assert resp.json()['message'] == 'Could not validate credentials'
