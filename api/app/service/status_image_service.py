from sqlmodel import select
from app.models import FileUploadPipeline, PipelineState
from app.core.deps import SessionDep
import uuid

def get_status_image_service(session:SessionDep):
    return StatusImageService(session)

class ImageStautsDto:
    def __init__(self, file_id: str, has_completed: bool, has_error: bool, error_message: str, state: int = -1):
        self.file_id = file_id
        self.has_completed = has_completed
        self.has_error = has_error
        self.error_message = error_message
        self.state = state
        
    file_id: str
    has_completed: bool
    has_error: bool
    error_message: str
    state: int

class StatusImageService:
    def __init__(self, session:SessionDep):
        self.session = session

    def get_image_status(self, file_id: str) -> ImageStautsDto:
        image_id = uuid.UUID(file_id)
        file_upload_pipeline_statement = select(FileUploadPipeline).where(FileUploadPipeline.file_upload_id == image_id)
        file_upload_pipeline: FileUploadPipeline = self.session.exec(file_upload_pipeline_statement).one_or_none()
        if file_upload_pipeline is None:
            return ImageStautsDto(file_id=file_id, has_completed=False, has_error=True, error_message="File not found")
        pipeline_state_statement = select(PipelineState).where(PipelineState.pipeline_id == file_upload_pipeline.pipeline_id)
        pipeline_state: PipelineState = self.session.exec(pipeline_state_statement).one_or_none()
        if pipeline_state is None:
            return ImageStautsDto(file_id=file_id, has_completed=False, has_error=True, error_message="Pipeline not found")
        return ImageStautsDto(file_id=file_id, has_completed=pipeline_state.has_completed, has_error=pipeline_state.has_error, error_message=pipeline_state.error_message, state=pipeline_state.state)