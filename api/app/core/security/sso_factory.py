from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from fastapi_sso.sso.base import SSOBase
from app.core.config import Settings

class SSOFactory():
    def __init__(self, settings: Settings):
        self.settings = settings
        
    def create(self, sso_type: str) -> SSOBase:
        if sso_type == "google":
            google_client_id = self.settings.GOOGLE_CLIENT_ID
            google_client_secret = self.settings.GOOGLE_CLIENT_SECRET
            google_redirect_uri = self.settings.GOOGLE_REDIRECT_URI
            return GoogleSSO(
                client_id=google_client_id,
                client_secret=google_client_secret,
                redirect_uri=google_redirect_uri,
                allow_insecure_http=True,
            )
        elif sso_type == "facebook":
            facebook_app_id = self.settings.FACEBOOK_APP_ID
            facebook_app_secret = self.settings.FACEBOOK_APP_SECRET
            facebook_redirect_uri = self.settings.FACEBOOK_REDIRECT_URI
            return FacebookSSO(
                app_id=facebook_app_id,
                app_secret=facebook_app_secret,
                redirect_uri=facebook_redirect_uri,
                allow_insecure_http=True,
            )
        else:
            raise ValueError(f"Unsupported SSO type: {sso_type}")