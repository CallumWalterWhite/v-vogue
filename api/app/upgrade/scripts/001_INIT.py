from sqlmodel import Session
from app.upgrade import UpgradeBase
from sqlalchemy import text

class INIT_UPGRADE(UpgradeBase):
    def __init__(self, session: Session):
        super().__init__(session)
    
    def upgrade(self, session: Session):
        print("Creating outboundmessage table...")
        session.exec(text("CREATE TABLE outboundmessage (id uuid PRIMARY KEY, content text, message_type text, correlation_id text, is_sent boolean)"))