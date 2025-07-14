import pytest
from fastapi import status
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.routes.payment import initiate_payment
from api.v1.models import User, BillingPlan, Payment
from api.v1.schemas.payment import InitiatePaymentSchema


client = TestClient(app)


# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

# Test User
@pytest.fixture
def test_user():
    user = User(
        id=str(uuid7().hex),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
    )
    return user

@pytest.fixture()
def test_bill_plan():
    bill_plan = BillingPlan(
        features=['One', 'Two'],
        plan_interval="one-off",
        plan_name="Plan 1",
        id=str(uuid7().hex),
        currency="NGN",
        price=3000
    )
    return bill_plan

@pytest.fixture
def mock_user_service(test_user):
    app.dependency_overrides[user_service.get_current_user] = lambda: test_user

@pytest.fixture
def access_token_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)


@pytest.fixture
def random_access_token():
    return user_service.create_access_token(user_id=str(uuid7().hex))


@pytest.mark.asyncio
@patch("api.v1.routes.payment.settings")
@patch("api.v1.routes.payment.requests.get")
async def test_verify_payment_successful(
    mock_get,
    mock_settings,
    mock_db_session,
    test_user,
    access_token_user,
    mock_user_service,
    test_bill_plan
):
    # Setup mocks
    mock_settings.FLUTTERWAVE_SECRET = "test_secret_key"
    mock_get.return_value.json.return_value = {
        "status": "success",
        "data": {
            "amount": 3000,
            "currency": "NGN",
            "tx_ref": "test123"
            }}

    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None
    mock_db_session.get.return_value = test_bill_plan

    response = client.get(
        f'api/v1/payments/verify/1234',
        headers={'Authorization': f'Bearer {access_token_user}'},
    )

    assert response.status_code == 200