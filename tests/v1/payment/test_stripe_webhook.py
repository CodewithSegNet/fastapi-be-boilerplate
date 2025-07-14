import pytest
from decimal import Decimal
from unittest.mock import patch
from uuid_extensions import uuid7
from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

from main import app
from api.db.database import get_db
from api.v1.models import User, BillingPlan, Payment
from api.v1.services.payment import payment_gateway_service
from api.v1.services.user_subscription import user_subscription_service


class StripeEvent:
    type = "checkout.session.completed"
    # data below is an actual 
    # data from a stripe test event
    data = {
        "object": {
            "id": "cs_test_a1VUSiYCvuxUnSTUaa8vdYEaTbfVWuvP8N7DtF8cpxpMqk7on1tlNfufmw",
            "object": "checkout.session",
            "after_expiration": None,
            "allow_promotion_codes": False,
            "amount_subtotal": 4999,
            "amount_total": 4999,
            "automatic_tax": {
            "enabled": False,
            "liability": None,
            "status": None
            },
            "billing_address_collection": "auto",
            "cancel_url": "https://stripe.com",
            "client_reference_id": None,
            "client_secret": None,
            "consent": None,
            "consent_collection": {
            "payment_method_reuse_agreement": None,
            "promotions": "none",
            "terms_of_service": "none"
            },
            "created": 1725101930,
            "currency": "usd",
            "currency_conversion": None,
            "custom_fields": [
            ],
            "custom_text": {
            "after_submit": None,
            "shipping_address": None,
            "submit": None,
            "terms_of_service_acceptance": None
            },
            "customer": "cus_QlLj7O144sr9er",
            "customer_creation": "if_required",
            "customer_details": {
            "address": {
                "city": None,
                "country": "NG",
                "line1": None,
                "line2": None,
                "postal_code": None,
                "state": None
            },
            "email": "chimeobioha@gmail.com",
            "name": "Chimeziri Obioha",
            "phone": None,
            "tax_exempt": "none",
            "tax_ids": [
            ]
            },
            "customer_email": None,
            "expires_at": 1725188329,
            "invoice": "in_1Ptp1zIiKrudT8J2WG2ygUnS",
            "invoice_creation": None,
            "livemode": False,
            "locale": "auto",
            "metadata": {
            "billing_plan_id": "premium_yearly",
            "platform_name": "tifi"
            },
            "mode": "subscription",
            "payment_intent": None,
            "payment_link": "plink_1PtmXfIiKrudT8J2yfZsynte",
            "payment_method_collection": "always",
            "payment_method_configuration_details": {
            "id": "pmc_1PthBwIiKrudT8J2JZ5UCemY",
            "parent": None
            },
            "payment_method_options": {
            "card": {
                "request_three_d_secure": "automatic"
            }
            },
            "payment_method_types": [
            "card",
            "link",
            "cashapp"
            ],
            "payment_status": "paid",
            "phone_number_collection": {
            "enabled": False
            },
            "recovered_from": None,
            "saved_payment_method_options": {
            "allow_redisplay_filters": [
                "always"
            ],
            "payment_method_remove": None,
            "payment_method_save": None
            },
            "setup_intent": None,
            "shipping_address_collection": None,
            "shipping_cost": None,
            "shipping_details": None,
            "shipping_options": [
            ],
            "status": "complete",
            "submit_type": "auto",
            "subscription": "sub_1Ptp1zIiKrudT8J2SD3qBtCN",
            "success_url": "https://tifi.tv/subscribe/success",
            "total_details": {
            "amount_discount": 0,
            "amount_shipping": 0,
            "amount_tax": 0
            },
            "ui_mode": "hosted",
            "url": None
        }
    }


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
        plan_interval="yearly",
        plan_name="Premium Yearly",
        id="premium_yearly",
        currency="usd",
        price=49.99
    )
    return bill_plan


@pytest.fixture()
def test_payment(test_user):
    payment = Payment(
        id=str(uuid7().hex),
        amount=49.99,
        currency="usd",
        status="completed",
        method="stripe",
        user_id=test_user.id,
        transaction_id=StripeEvent.data['object']['id'],
        created_at=datetime.now(tz=timezone.utc)
    )
    return payment


@pytest.mark.asyncio
@patch("api.v1.services.user_subscription.UserSubscriptionService.get_sub_start_and_end_datetime")
@patch("api.v1.services.user_subscription.UserSubscriptionService.create")
@patch("api.v1.services.payment.PaymentService.create")
@patch("api.v1.routes.payment.get_model_by_params")
@patch("api.v1.services.payment.PaymentService.fetch_by_params")
@patch("api.v1.routes.payment.bp_service")
@patch("api.v1.services.payment.stripe")
@patch("api.v1.services.payment.PaymentGatewayService.get_stripe_webhook_event")
async def test_subscription_success(
    mock_get_stripe_webhook_event,
    mock_stripe,
    mock_bp_service,
    mock_payment_fetch_by_params,
    mock_get_model_by_params,
    mock_payment_create,
    mock_user_subscription_create,
    mock_get_sub_start_and_end_datetime,
    mock_db_session,
    test_user,
    test_bill_plan
):
    # set value for mocks
    mock_get_stripe_webhook_event.return_value = StripeEvent
    mock_stripe.api_key = "test_secret_key"
    mock_bp_service.fetch.return_value = test_bill_plan
    mock_payment_fetch_by_params.return_value = None
    mock_get_model_by_params.return_value = test_user

    start_date = datetime.now(tz=timezone.utc)
    end_date = start_date + timedelta(days=360)
    mock_get_sub_start_and_end_datetime.return_value = (start_date, end_date)

    response = client.post('api/v1/payments/stripe/webhook')

    assert response.status_code == 201

    event_data = StripeEvent.data['object']
    
    # test that call to create payment was made
    mock_payment_create.assert_called_once_with(
        mock_db_session,
        {
            "user_id": test_user.id,
            "transaction_id": event_data['id'],
            "amount": Decimal(format(test_bill_plan.price, ".2f")),
            "currency": event_data['currency'],
            "status": "completed",
            "method": "stripe",
        }
    )
    
    # test that call to create user subscription was made
    mock_user_subscription_create.assert_called_once_with(
        mock_db_session,
        {
            "start_date": start_date,
            "billing_plan_id": test_bill_plan.id,
            "user_id": test_user.id,
            "end_date": end_date
        }
    )


@pytest.mark.asyncio
@patch("api.v1.services.payment.PaymentService.fetch_by_params")
@patch("api.v1.services.payment.stripe")
@patch("api.v1.services.payment.PaymentGatewayService.get_stripe_webhook_event")
async def test_subscription_unsuccessful(
    mock_get_stripe_webhook_event,
    mock_stripe,
    mock_payment_fetch_by_params,
    mock_db_session,
    test_user,
    test_bill_plan
):
    # set value for mocks
    mock_get_stripe_webhook_event.return_value = StripeEvent
    mock_stripe.api_key = "test_secret_key"
    mock_payment_fetch_by_params.return_value = None

    # WRONG AMOUNT
    test_bill_plan.price = 50  # instead of 49.99
    mock_db_session.get.return_value = test_bill_plan
    response = client.post('api/v1/payments/stripe/webhook')
    assert response.status_code == 400
    # reset amount to previous state
    test_bill_plan.price = 49.99


    # WRONG CURRENCY
    test_bill_plan.currency = "NGN" # instead of `USD`
    mock_db_session.get.return_value = test_bill_plan
    response = client.post('api/v1/payments/stripe/webhook')
    assert response.status_code == 400
    # reset currency to previous state
    test_bill_plan.currency = "USD"


    # NO BILLING PLAN FOUND
    mock_db_session.get.return_value = None
    response = client.post('api/v1/payments/stripe/webhook')
    assert response.status_code == 404
    # reset billing plan to previous state
    mock_db_session.get.return_value = test_bill_plan


    # PAYMENT OBJECT ALREADY EXIST
    # i.e: One with transaction_id==event id
    mock_payment_fetch_by_params.return_value = test_payment
    response = client.post('api/v1/payments/stripe/webhook')
    assert response.status_code == 200  # 200 response is correct, payment already exist
    # reset payment to previous state
    mock_payment_fetch_by_params.return_value = None


    # WRONG EVENT TYPE
    StripeEvent.type = "unhandled.event"
    response = client.post('api/v1/payments/stripe/webhook')
    assert response.status_code == 200
    # reset event type to previous state
    StripeEvent.type = "checkout.session.completed"


    # WRONG SUCCESS URL
    StripeEvent.data['object']['success_url'] = "http://tifi.tv/subscribe/success"
    response = client.post('api/v1/payments/stripe/webhook')
    assert response.status_code == 200
    # reset success url to previous state
    StripeEvent.data['object']['success_url'] = "https://tifi.tv/subscribe/success"


def test_stripe_payment_related_functions():
    
    # TEST MONTHLY SUBSCRIPTION DURATION
    start_date, end_date = user_subscription_service.get_sub_start_and_end_datetime("monthly")
    assert (end_date - start_date).days == 30
    

    # TEST YEARLY SUBSCRIPTION DURATION
    start_date, end_date = user_subscription_service.get_sub_start_and_end_datetime("yearly")
    assert (end_date - start_date).days == 360
    

    # TEST FREE SUBSCRIPTION DURATION
    start_date, end_date = user_subscription_service.get_sub_start_and_end_datetime("free")
    assert (end_date - start_date).days == 360


    # TEST NORMALISE STRIPE AMOUNT
    def two_deci(num):
        return Decimal(format(num, ".2f"))
    # ....................................
    assert payment_gateway_service.normalise_stripe_amount(49, to_stripe=True) == two_deci(4900)
    assert payment_gateway_service.normalise_stripe_amount(4900, from_stripe=True) == two_deci(49)

    assert payment_gateway_service.normalise_stripe_amount(49.99, to_stripe=True) == two_deci(4999)
    assert payment_gateway_service.normalise_stripe_amount(4999, from_stripe=True) == two_deci(49.99)

    assert payment_gateway_service.normalise_stripe_amount(Decimal(49.99), to_stripe=True) == two_deci(4999)
    assert payment_gateway_service.normalise_stripe_amount(Decimal(4999), from_stripe=True) == two_deci(49.99)

    with pytest.raises(HTTPException) as e_info:   
        payment_gateway_service.normalise_stripe_amount(49)
        e_info.type is HTTPException