from fastapi import APIRouter
from api.v1.routes.api_status import api_status
from api.v1.routes.auth import auth
from api.v1.routes.user import user_router

from api.v1.routes.google_auth import google_auth
from api.v1.routes.data_privacy import privacy
from api.v1.routes.request_password import pwd_reset
from api.v1.routes.profile import profile
from api.v1.routes.notification import notification
from tests.run_all_test import test_rout


api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(api_status)
api_version_one.include_router(auth)
api_version_one.include_router(google_auth)
api_version_one.include_router(user_router)
api_version_one.include_router(profile)
api_version_one.include_router(pwd_reset)
api_version_one.include_router(notification)
api_version_one.include_router(privacy)
api_version_one.include_router(test_rout)
