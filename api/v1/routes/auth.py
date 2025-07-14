from datetime import timedelta
from fastapi import (
    BackgroundTasks,
    Depends,
    status,
    APIRouter,
    Response,
    Request,
    Query,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models import User
from api.v1.schemas.user import (
    LoginRequest,
    UserCreate,
    RegisterUserResponse,
    RefreshAccessTokenResponse,
    LogoutResponse,
    MagicLinkResponse
)
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.schemas.request_password_reset import RequestEmail
from api.v1.services.request_pwd import reset_service as magic_link_service
from api.v1.services.email_sending import email_sending_service


auth = APIRouter(prefix="/auth", tags=["Authentication"])

@auth.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterUserResponse,
)
def register(
    background_tasks: BackgroundTasks,
    request: Request,
    response: Response,
    user_schema: UserCreate,
    db: Session = Depends(get_db),
):
    """Endpoint for a user to register their account"""

    # Create user account
    user = user_service.create(db=db, schema=user_schema)

    user_subscription = billing_plan_service.subscribe_user_to_free_plan(db=db, user=user)

    # Create access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    # Send email in the background
    email_sending_service.send_welcome_email(request, background_tasks, user)

    response = JSONResponse(
        status_code=201,
        content={
            "status_code": 201,
            "message": "User created successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "data": {
                "user": jsonable_encoder(
                    user, 
                    exclude=["password", "is_deleted", "updated_at"]
                ),
                "user_subscription" : jsonable_encoder(
                    user_subscription , 
                    exclude=["user_id"]
                )
            },
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=60),
        httponly=True,
        secure=True,
        samesite="none",
    )
    
    TelexIntegration(webhook_id='80592c026382').push_message(
        event_name='New signup',
        message=f'New signup detected from {user.email}\nUser details: {user.to_dict()}'
    )

    return response


@auth.post(
    path="/register-super-admin",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterUserResponse,
)
def register_as_super_admin(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Endpoint for super admin creation"""

    user = user_service.create_admin(db=db, schema=user)

    # Create access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = JSONResponse(
        status_code=201,
        content={
            "status_code": 201,
            "message": "User created successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "data": {
                "user": jsonable_encoder(
                    user, exclude=["password", "is_deleted", "updated_at"]
                )
            },
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=60),
        httponly=True,
        secure=True,
        samesite="none",
    )
    
    TelexIntegration(webhook_id='80592c026382').push_message(
        event_name='New superadmin signup',
        message=f'New signup detected from {user.email}\nUser details: {user.to_dict()}'
    )

    return response


@auth.post(
    "/login", status_code=status.HTTP_200_OK, response_model=RegisterUserResponse
)
def login(login_request: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Endpoint to log in a user"""

    # Authenticate the user
    user = user_service.authenticate_user(
        db=db, email=login_request.email, password=login_request.password
    )

    # Generate access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = JSONResponse(
        status_code=200,
        content={
            "status_code": 200,
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "data": {
                "user": jsonable_encoder(
                    user, 
                    exclude=["password", "is_deleted", "updated_at"]
                )
            },
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=30),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response


@auth.post("/logout", status_code=status.HTTP_200_OK, response_model=LogoutResponse)
def logout(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to log a user out of their account"""

    response = success_response(
        status_code=200, 
        message="User logged put successfully"
    )

    # Delete refresh token from cookies
    response.delete_cookie(key="refresh_token")

    return response


@auth.post(
    "/refresh-access-token", 
    status_code=status.HTTP_200_OK, 
    response_model=RefreshAccessTokenResponse
)
def refresh_access_token(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    """Endpoint to log a user out of their account"""

    # Get refresh token
    current_refresh_token = request.cookies.get("refresh_token")

    # Create new access and refresh tokens
    access_token, refresh_token = user_service.refresh_access_token(
        current_refresh_token=current_refresh_token
    )

    response = response = JSONResponse(
        status_code=200,
        content={
            "status_code": 200,
            "message": "Tokens refreshed successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=30),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response


@auth.post("/magic-link", status_code=status.HTTP_200_OK, response_model=MagicLinkResponse)
async def request_magic_link(
    magic_link_request_schema: RequestEmail,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    
    user, link = await magic_link_service.create(
        magic_link_request_schema,
        db,
        url='/magic-link/verify',
    )

    # Send email
    email_sending_service.send_magic_link_email(
        request=request,
        background_tasks=background_tasks,
        user=user,
        magic_link_url=link
    )

    return success_response(
        message='Magic link sent successfully',
        status_code=200,
        data={"magic-link": link}
    )


@auth.get(
    "/magic-link/verify",
    status_code=status.HTTP_200_OK,
    response_model=RegisterUserResponse,
)
def verify_magic_link(token: str = Query(...), db: Session = Depends(get_db)):
    """Endpoint to verify a magic link"""

    # verify user magic link
    user = magic_link_service.verify_magic_link(token=token, session=db)

    # Generate access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = JSONResponse(
        status_code=200,
        content={
            "status_code": 200,
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "data": {
                "user": jsonable_encoder(
                    user, 
                    exclude=["password", "is_deleted", "updated_at"]
                )
            },
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=30),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response
