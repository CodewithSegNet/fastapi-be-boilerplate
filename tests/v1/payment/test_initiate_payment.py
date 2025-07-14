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


@pytest.fixture
def mock_user_service():
    with patch("api.v1.services.user.user_service", autospec=True) as user_service_mock:
        yield user_service_mock


@pytest.fixture()
def test_bill_plan():
    bill_plan = BillingPlan(
        features=['One', 'Two'],
        plan_interval="one-off",
        plan_name="Plan 1",
        id=str(uuid7().hex),
        currency="NGN",
        price=5000
    )
    return bill_plan


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
def test_payment(test_user):
    payment = Payment(
        id=str(uuid7().hex),
        amount=5000.00,
        currency="NGN",
        status="completed",
        method="flutterwave",
        user_id=test_user.id,
        transaction_id=str(uuid7().hex),
        created_at=datetime.now(tz=timezone.utc)
    )

    return payment


@pytest.fixture()
def mock_initiate_payment_schema(test_user, test_bill_plan):
    return InitiatePaymentSchema(
        billing_plan_id=test_bill_plan.id,
        payment_gateway="flutterwave",
        redirect_url="http://example.com"
    )


@pytest.fixture()
def mock_initiate_payment_schema_stripe(test_user, test_bill_plan):
    return InitiatePaymentSchema(
        billing_plan_id=test_bill_plan.id,
        payment_gateway="stripe",
        redirect_url="http://example.com"
    )


@pytest.fixture
def access_token_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)


@pytest.fixture
def random_access_token():
    return user_service.create_access_token(user_id=str(uuid7().hex))


@pytest.mark.asyncio
@patch("api.v1.routes.payment.settings")
@patch("api.v1.routes.payment.requests.post")
@patch("api.v1.routes.payment.uuid7")
async def test_initiate_payment_successful(
    mock_uuid7,
    mock_post,
    mock_settings,
    mock_db_session,
    test_user,
    test_bill_plan,
    access_token_user,
    mock_initiate_payment_schema_stripe,
    mock_initiate_payment_schema
):
    # Setup mocks
    uuid_for_tx_ref = uuid7().hex
    mock_settings.STRIPE_SECRET = "test_secret_key"
    mock_settings.FLUTTERWAVE_SECRET = "test_secret_key"
    mock_uuid7.return_value = uuid_for_tx_ref
    mock_post.return_value.json.return_value = {"data": {"link": "http://payment.url"}}

    mock_db_session.query().filter().first.return_value = test_user
    mock_db_session.get.return_value = test_bill_plan

    req = await initiate_payment(
        mock_initiate_payment_schema, test_user, mock_db_session)

    assert req.status_code == status.HTTP_200_OK


def test_initiate_payment_unsuccessful(
    mock_db_session,
    test_user,
    test_bill_plan,
    access_token_user,
):
    headers = {"Authorization": f"Bearer {access_token_user}"}
    mock_db_session.query().filter().first.return_value = test_user
    mock_db_session.query().get.return_value = test_bill_plan
    post_url = "/api/v1/payments/initiate"
    data = {
        'billing_plan_id': test_bill_plan.id,
        'payment_gateway': "anothergateway",
        'redirect_url': "example.com"
    }

    # NON-STRIPE/FLUTTERWAVE
    response = client.post(post_url, json=data, headers=headers)
    assert response.status_code == 403
    assert response.json()["message"] == "Only ['stripe', 'flutterwave'] supported for now"
    # reset url to correct one
    data.update({'payment_gateway': 'flutterwave'})

    # WRONG billing plan id
    mock_db_session.get.return_value = None
    response = client.post(post_url, json=data, headers=headers)
    assert response.status_code == 404
    assert response.json()["message"] == "BillingPlan does not exist"
    # reset billing plan mock to correct one
    mock_db_session.get.return_value = test_bill_plan

    # NO AUTH
    response = client.post(post_url, json=data)
    assert response.status_code == 401
    assert response.json()['message'] == 'Not authenticated'
