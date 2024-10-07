from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from fastapi_sso.sso.base import SSOBase
from app.core.config import BaseSettings

class SSOFactory():
    def __init__(self, settings: BaseSettings):
        self.settings = settings

    def create(self, sso_type: str) -> SSOBase:
        if sso_type == "google":
            return GoogleSSO(self.config)
        elif sso_type == "facebook":
            return FacebookSSO(self.config)
        else:
            raise ValueError(f"Unsupported SSO type: {sso_type}")