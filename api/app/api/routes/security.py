from urllib.request import Request
from fastapi import APIRouter
from app.core.security import google_sso, facebook_sso

router = APIRouter("/security")

@router.get("/login/google")
async def google_login():
    """Redirect the user to the Google SSO login."""
    with google_sso:
        return await google_sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})

@router.get("/auth/google/callback")
async def google_callback(request: Request):
    with google_sso:
        user = await google_sso.verify_and_process(request)
    return user

@router.get("/login/facebook")
async def google_login():
    """Redirect the user to the Google SSO login."""
    with facebook_sso:
        return await google_sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})

@router.get("/auth/facebook/callback")
async def google_callback(request: Request):
    with facebook_sso:
        user = await facebook_sso.verify_and_process(request)
    return user
