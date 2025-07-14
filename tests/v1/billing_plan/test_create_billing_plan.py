# from unittest.mock import patch, MagicMock
# from fastapi.testclient import TestClient
# from api.db.database import get_db
# from sqlalchemy.orm import Session
# from uuid_extensions import uuid7
# import pytest

# from main import app
# from api.v1.models.user import User
# from api.v1.services.user import user_service
# from api.v1.models.billing_plan import BillingPlan


# client = TestClient(app)


# @pytest.fixture
# def mock_db_session(mocker):
#     db_session_mock = mocker.MagicMock(spec=Session)
#     app.dependency_overrides[get_db] = lambda: db_session_mock
#     return db_session_mock


# @pytest.fixture
# def mock_user_service():
#     with patch("api.v1.services.user.user_service", autospec=True) as user_service_mock:
#         yield user_service_mock


# @pytest.fixture
# def mock_billing_plan_service(mock_db_session):
#     with patch("api.v1.services.billing_plan.billing_plan_service", autospec=True
#                ) as billing_plan_service_mock:
#         yield billing_plan_service_mock


# @pytest.fixture
# def test_user():
#     return User(
#         id=str(uuid7().hex),
#         email="testuser@gmail.com",
#         password="hashedpassword",
#         first_name="test",
#         last_name="user",
#         is_active=True,
#         is_superadmin=True,
#     )


# @pytest.fixture
# def test_billing_plan():
#     return BillingPlan(
#         id=str(uuid7().hex),
#         plan_name="one",
#         price=5000,
#         access_limit=15,
#         plan_interval="monthly",
#         currency="NGN",
#         features=["string", "string"]
#     )


# @pytest.fixture
# def access_token_user(test_user):
#     return user_service.create_access_token(user_id=test_user.id)


# @pytest.fixture
# def random_access_tokenr():
#     return user_service.create_access_token(user_id='hshsdgdgdgdgdgdg')


# def make_request(token):
#     data = {
#         "plan_name": "one",
#         "price": 5000,
#         "plan_interval": "monthly",
#         "access_limit":15,
#         "currency": "NGN",
#         "features": [
#             "string", "string"
#         ]
#     }
#     return client.post(
#         f"/api/v1/billing-plans", json=data,
#         headers={"Authorization": f"Bearer {token}"}
#     )


# # Test for successful creation
# @patch("api.v1.services.billing_plan.uuid7")
# def test_create_billing_plan_successful(
#     mock_uuid7,
#     mock_db_session,
#     test_user,
#     test_billing_plan,
#     access_token_user,
#     mock_billing_plan_service
# ):
#     mock_uuid7.return_value = test_billing_plan.id
#     mock_db_session.query().filter().first.return_value = test_user
#     mock_billing_plan_service.create.return_value = test_billing_plan

#     resp = make_request(access_token_user)
#     resp_d = resp.json()
#     assert resp.status_code == 201
#     assert resp_d['success'] == True
#     assert resp_d['message'] == "Billing plan created successfully."

#     bp_data = resp_d['data']
#     assert bp_data['id'] == test_billing_plan.id
#     assert bp_data['price'] == test_billing_plan.price
#     assert bp_data['currency'] == test_billing_plan.currency
#     assert bp_data['features'] == test_billing_plan.features
#     assert bp_data['plan_name'] == test_billing_plan.plan_name
#     assert bp_data['plan_interval'] == test_billing_plan.plan_interval


# # Test for unsuccessful creation
# def test_create_billing_plan_unsuccessful(
#     mock_db_session,
#     test_user,
#     test_billing_plan,
#     access_token_user,
#     mock_billing_plan_service
# ):
#     mock_db_session.query().filter().first.return_value = test_user

#     # NON-SUPERADMIN
#     test_user.is_superadmin = False
#     resp = make_request(access_token_user)
#     assert resp.status_code == 403
#     assert resp.json()[
#         "message"] == "You do not have permission to access this resource"

#     # INVALID AUTH
#     test_user.is_superadmin = True
#     resp = make_request(random_access_tokenr)
#     assert resp.status_code == 401
#     assert resp.json()['message'] == 'Could not validate credentials'
