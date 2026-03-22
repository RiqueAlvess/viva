from fastapi import APIRouter

from app.api.v1 import auth, admin, companies, users, campaigns, invitations, survey, dashboard, reports

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(companies.router, prefix="/companies", tags=["companies"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
router.include_router(invitations.router, prefix="/invitations", tags=["invitations"])
router.include_router(survey.router, prefix="/survey", tags=["survey"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
router.include_router(reports.router, prefix="/reports", tags=["reports"])
