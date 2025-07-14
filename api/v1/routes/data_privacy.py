from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.data_privacy import DataPrivacySettingUpdate
from api.v1.services.data_privacy import data_privacy_service
from api.db.database import get_db
from api.v1.services.user import user_service


privacy = APIRouter(prefix="/data-privacy-settings", tags=["Data Privacy"])

@privacy.post("", response_model=DataPrivacySettingUpdate)
def create_or_update_data_privacy_settings(
    privacy_settings: DataPrivacySettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    updated_privacy_settings = data_privacy_service.update(
        db=db, user=current_user, schema=privacy_settings
    )
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Data privacy settings updated successfully",
        data=updated_privacy_settings
    )

@privacy.get("", response_model=DataPrivacySettingUpdate)
def fetch_data_privacy_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    privacy_settings = data_privacy_service.fetch(db=db, user=current_user)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Data privacy settings retrieved successfully",
        data=privacy_settings
    )