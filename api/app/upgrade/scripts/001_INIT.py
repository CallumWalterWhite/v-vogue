from sqlmodel import SQLModel, Session
from app.upgrade import UpgradeBase
from app.models import FileUploadMetadata, OutboundMessage, FileUpload, PipelineState, FileUploadPipeline, ModelImageMetadata

class INIT_UPGRADE(UpgradeBase):
    def __init__(self, session: Session):
        super().__init__(session)
    
    def upgrade(self, session: Session):
        SQLModel.metadata.create_all(session.get_bind(), tables=[OutboundMessage.__table__, FileUpload.__table__, PipelineState.__table__, FileUploadPipeline.__table__, FileUploadMetadata.__table__, ModelImageMetadata.__table__])