# import pytest
# from uuid_extensions import uuid7
# from sqlalchemy.orm import Session
# from unittest.mock import MagicMock
# from datetime import datetime, timezone
# from fastapi.testclient import TestClient

# from main import app
# from api.db.database import get_db
# from api.v1.models import User, BillingPlan
# from api.v1.services.user import user_service

# client = TestClient(app)

# # Mock database
# @pytest.fixture
# def mock_db_session(mocker):
#     db_session_mock = mocker.MagicMock(spec=Session)
#     app.dependency_overrides[get_db] = lambda: db_session_mock
#     return db_session_mock

# # Test User
# @pytest.fixture
# def test_user():
#     return User(
#         id=str(uuid7().hex),
#         email="testuser@gmail.com",
#         password="hashedpassword",
#         first_name="test",
#         last_name="user",
#         is_active=True,
#     )


# @pytest.fixture
# def test_billing_plan():
#     return BillingPlan(
#         id=str(uuid7().hex),
#         plan_name="one",
#         price=5000,
#         currency="NGN",
#         plan_interval="monthly",
#         features=["string", "string"],
#         created_at=datetime.now(tz=timezone.utc)
#     )

# @pytest.fixture
# def access_token_user(test_user):
#     return user_service.create_access_token(user_id=test_user.id)

# @pytest.fixture
# def random_access_token():
#     return user_service.create_access_token(user_id=str(uuid7().hex))


# # Test for successful retrieve of billing_plans
# # NO AUTHENTICATION
# def test_get_billing_plans_successfully(
#     mock_db_session,
#     test_user,
#     test_billing_plan,
#     access_token_user
# ):
#     # Mock the query for getting user
#     mock_db_session.query().filter().first.return_value = test_user

#     # TEST A SINGLE BILLING PLAN FOR #

#     # Mock the query for billing-plans
#     mock_db_session.query().all.return_value = [test_billing_plan]

#     # Make request
#     response = client.get("/api/v1/billing-plans")

#     resp_d = response.json()

#     assert response.status_code == 200
#     assert resp_d['success'] is True
#     assert resp_d['message'] == "Billing plans fetched successfully."

#     billing_plans = resp_d['data']['billing_plans']
#     assert len(billing_plans) == 1

#     plan = billing_plans[0]
#     assert plan['id'] == test_billing_plan.id
#     assert plan['plan_name'] == test_billing_plan.plan_name
#     assert plan['currency'] == test_billing_plan.currency
#     assert plan['price'] == test_billing_plan.price
#     assert plan['features'] == test_billing_plan.features
#     assert datetime.fromisoformat(plan['created_at']) == test_billing_plan.created_at

#     # RESET MOCK BILLING PLANS MULTIPLE RESULT #

#     # Mock the query for billing_plans, this time for 5 billing_plans
#     five_billing_plans = [
#         test_billing_plan, test_billing_plan, test_billing_plan, 
#         test_billing_plan, test_billing_plan
#     ]
#     mock_db_session.query().all.return_value = five_billing_plans

#     # Make request
#     response = client.get("/api/v1/billing-plans")

#     resp_d = response.json()

#     assert response.status_code == 200
#     assert resp_d['success'] is True
#     assert resp_d['message'] == "Billing plans fetched successfully."

#     billing_plans = resp_d['data']['billing_plans']
#     assert len(billing_plans) == 5


# # Test that authenticated requests also goes through
# def test_for_authenticated_request_goes_through(
#     mock_db_session,
#     test_user,
#     test_billing_plan,
#     access_token_user
# ):
#     # Mock the query for getting user
#     mock_db_session.query().filter().first.return_value = test_user

#     # Mock the query for billing-plans
#     mock_db_session.query().all.return_value = [test_billing_plan]

#     # Make request
#     headers = {'Authorization': f'Bearer {access_token_user}'}
#     response = client.get("/api/v1/billing-plans", headers=headers)

#     resp_d = response.json()

#     assert response.status_code == 200
#     assert resp_d['success'] is True
#     assert resp_d['message'] == "Billing plans fetched successfully."

#     billing_plans = resp_d['data']['billing_plans']
#     assert len(billing_plans) == 1


# # Test for no billing plans found
# def test_for_no_billing_plans_found(
#     mock_db_session,
#     test_user,
#     test_billing_plan,
#     access_token_user
# ):
#     # Mock the query for getting user
#     mock_db_session.query().filter().first.return_value = test_user

#     # Mock the query for billing_plans
#     mock_db_session.query().all.return_value = []

#     # Make request
#     headers = {'Authorization': f'Bearer {access_token_user}'}
#     response = client.get("/api/v1/billing-plans", headers=headers)

#     assert response.status_code == 200
#     assert response.json()['success'] is True
#     assert response.json()['message'] == "Billing plans fetched successfully."
