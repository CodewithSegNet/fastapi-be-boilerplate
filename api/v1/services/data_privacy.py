from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.models.data_privacy import DataPrivacySetting


class DataPrivacyService:
    """Data Privacy Services"""

    def create(self, user: User, db: Session):
        try:
            data_privacy = DataPrivacySetting(user_id=user.id)
            db.add(data_privacy)
            db.commit()
            db.refresh(data_privacy)
            return data_privacy
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create data privacy settings: {str(e)}"
            )

    def fetch(self, db: Session, user: User):
        if not user.data_privacy_setting:
            return self.create(user, db)
        return user.data_privacy_setting

    def update(self, db: Session, user: User, schema):
        try:
            data_privacy_setting = self.fetch(db=db, user=user)

            # Update the fields with the provided schema data
            update_data = schema.dict(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(data_privacy_setting, key):
                    setattr(data_privacy_setting, key, value)

            db.commit()
            db.refresh(data_privacy_setting)
            return data_privacy_setting
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update data privacy settings: {str(e)}"
            )

    def delete(self):
        pass


data_privacy_service = DataPrivacyService()