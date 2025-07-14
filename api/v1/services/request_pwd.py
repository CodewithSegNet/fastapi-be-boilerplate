from sqlalchemy.orm import Session
from fastapi import HTTPException, Request, Query, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas import request_password_reset
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from passlib.context import CryptContext
from typing import Optional
from api.utils.settings import settings
from api.v1.models.user import User
from api.v1.services.user import user_service


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token serializer
SECRET_KEY = settings.SECRET_KEY
FRONTEND_BASE_URL = settings.FRONTEND_MAGICLINK_URL
serializer = URLSafeTimedSerializer(SECRET_KEY)


# Helper functions
def create_token(email: str) -> str:
    return serializer.dumps(email, salt=SECRET_KEY)


def verify_token(token: str, expiration: int = 3600) -> Optional[str]:
    try:
        email = serializer.loads(token, salt=SECRET_KEY, max_age=expiration)
        return email
    except (BadSignature, SignatureExpired):
        return None


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class RequestPasswordService:
    
    @staticmethod
    async def create(
        schema: request_password_reset.RequestEmail,
        session: Session,
        url: str
    ):

        user = session.query(User).filter_by(email=schema.user_email).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        token = create_token(schema.user_email)
       
        link = f"{FRONTEND_BASE_URL}{url}?token={token}"

        return user, link


    @staticmethod
    def process_reset_link(token: str = Query(...), session: Session = Depends(get_db)):

        email = verify_token(token)

        if not email:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user = session.query(User).filter_by(email=email).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return success_response(
            message=f"token is valid for user {email}",
            status_code=status.HTTP_302_FOUND,
        )
    
    @staticmethod
    def verify_magic_link(token: str = Query(...), session: Session = Depends(get_db)):

        email = verify_token(token)

        if not email:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user = session.query(User).filter_by(email=email).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    @staticmethod
    def reset_password(
        data: request_password_reset.ResetPassword = Depends(),
        token: str = Query(...),
        session: Session = Depends(get_db),
    ):
        try:
            email = verify_token(token)

            if not email:
                raise HTTPException(status_code=400, detail="Invalid or expired token")

            user = session.query(User).filter_by(email=email).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            if data.new_password != data.confirm_password:
                raise HTTPException(status_code=400, detail="Passwords do not match")

            user.password = get_password_hash(data.new_password)
            session.commit()

            return user
        
        except SQLAlchemyError as e:
            session.rollback()  # Rollback the session in case of an error
            print(f"Database error: {e}")  # Log the error for debugging purposes
            raise HTTPException(
                status_code=500,
                detail="An error occurred while processing your request.",
            )
        

    @staticmethod
    def reset_user_password(
        data: request_password_reset.ResetPassword = Depends(),
        session: Session = Depends(get_db),
        user: User = None
    ):
        
        try:
            if data.new_password != data.confirm_password:
                raise HTTPException(status_code=400, detail="Passwords do not match")

            user.password = get_password_hash(data.new_password)
            session.commit()

            return success_response(
                message="Password has been reset successfully",
                status_code=status.HTTP_200_OK,
            )

        except SQLAlchemyError as e:
            session.rollback()  # Rollback the session in case of an error
            print(f"Database error: {e}")  # Log the error for debugging purposes
            raise HTTPException(
                status_code=500,
                detail="An error occurred while processing your request.",
            )


reset_service = RequestPasswordService()
