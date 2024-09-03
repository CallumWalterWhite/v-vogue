from app.core.config import settings

class Publisher():
    def __init__(self):
        if settings.IS_LOCAL_MESSAGING:
            self.internal_request 
        else:
            pass