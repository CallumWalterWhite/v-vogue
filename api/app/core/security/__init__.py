from app.core.security.sso_factory import SSOFactory
from app.core.config import settings

ssoFactory = SSOFactory(settings)

global google_sso
google_sso = ssoFactory.create("google")
global facebook_sso
facebook_sso = ssoFactory.create("facebook")