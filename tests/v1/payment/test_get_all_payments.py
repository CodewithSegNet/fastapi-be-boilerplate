import pytest
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app
from api.db.database import get_db
from api.v1.models import User, Payment
from api.v1.services.user import user_service

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
def mock_payment_service():
    with patch("api.v1.services.payment.payment_service", autospec=True) as payment_service_mock:
        yield payment_service_mock

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


@pytest.fixture
def access_token_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)

@pytest.fixture
def random_access_tokenr():
    return user_service.create_access_token(user_id='hshsdgdgdgdgdgdg')

def make_request(token):
    return client.get(
        "/api/v1/payments", 
        headers={"Authorization": f"Bearer {token}"}
    )


# Test for successful retrieve of payments
def test_get_payments_successful(
    mock_db_session,
    test_user,
    test_payment,
    access_token_user
):
    # Mock the query for getting user
    mock_db_session.query().filter().first.return_value = test_user

    # TEST A SINGLE PRODUCT FOR 1-PAGE RESULT #

    # Mock the query for payments
    mock_db_session.query().all.return_value = [test_payment]

    # Make request
    response = make_request(access_token_user)
    resp_d = response.json()

    print(resp_d)
    assert response.status_code == 200
    assert resp_d['success'] is True
    assert resp_d['message'] == "Payments fetched successfully"

    pagination = resp_d['data']['pagination']
    assert pagination['pages'] == 1
    assert pagination['limit'] == 10
    assert pagination['offset'] == 0
    assert pagination['total_items'] == 1

    payments = resp_d['data']['payments']
    assert len(payments) == 1

    pay = payments[0]
    assert pay['id'] == test_payment.id
    assert pay['status'] == test_payment.status
    assert pay['method'] == test_payment.method
    assert pay['user_id'] == test_payment.user_id
    assert pay['currency'] == test_payment.currency
    assert float(pay['amount']) == test_payment.amount
    assert pay['transaction_id'] == test_payment.transaction_id
    assert datetime.fromisoformat(pay['created_at']) == test_payment.created_at

    # RESET MOCK PRODUCTS TO SIMULATE MULTI-PAGE RESULT #

    # Mock the query for payments, this time for 5 payments
    five_payments = [test_payment, test_payment, test_payment, test_payment, test_payment]
    mock_db_session.query().all.return_value = five_payments

    # Make request
    response = make_request(access_token_user)

    resp_d = response.json()

    assert response.status_code == 200
    assert resp_d['success'] is True
    assert resp_d['message'] == "Payments fetched successfully"

    pagination = resp_d['data']['pagination']
    assert pagination['pages'] == 1
    assert pagination['limit'] == 10
    assert pagination['offset'] == 0
    assert pagination['total_items'] == 5

    payments = resp_d['data']['payments']
    assert len(payments) == 5


# Test for un-authenticated request
def test_for_unauthenticated_requests(
    mock_db_session,
    test_user,
    # test_payment,
    access_token_user
):
    # Mock the query for getting user
    mock_db_session.query().filter().first.return_value = test_user

    # WRONG AUTH TOKEN
    response = make_request(random_access_tokenr)
    assert response.status_code == 401
    assert response.json()['message'] == "Could not validate credentials"

    # NO AUTH TOKEN
    response = client.get("/api/v1/payments")
    assert response.status_code == 401
    assert response.json()['message'] == "Not authenticated"

    # NON-SUPERADMIN
    test_user.is_superadmin = False
    resp = make_request(access_token_user)
    assert resp.status_code == 403
    assert resp.json()[
        "message"] == "You do not have permission to access this resource"


# Test for no payment 
def test_for_payments_not_found(
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
    assert resp_d['message'] == "Payments fetched successfully"
    assert resp_d['data']['payments'] == []

    pagination = resp_d['data']['pagination']
    assert pagination['pages'] == 0
    assert pagination['limit'] == 10
    assert pagination['offset'] == 0
    assert pagination['total_items'] == 0
