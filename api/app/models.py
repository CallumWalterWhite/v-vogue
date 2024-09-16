import datetime
import uuid
from sqlmodel import Field, Relationship, SQLModel

#TODO: add all foreign keys...... bad on me

class MessageBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str | None = Field(default=None, max_length=255)
    message_type: str | None = Field(default=None, max_length=255)
    correlation_id: str | None = Field(default=None, max_length=255)
    timestamp: int | None = Field(default=datetime.datetime.now().timestamp())

class OutboundMessage(MessageBase, table=True):
    is_sent: bool | None = Field(default=False)

class InboundMessage(MessageBase, table=True):
    is_success: bool | None = Field(default=None)

class UpgradeManifest(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    script: str | None = Field(default=None, max_length=255)    

class FileUpload(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    filename: str | None = Field(default=None, max_length=255)
    fullpath: str | None = Field(default=None, max_length=255)
    fileextension: str | None = Field(default=None, max_length=255)
    type: str | None = Field(default=None, max_length=255)

class FileUploadMetadata(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    file_upload_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    width: int | None = Field(default=None)
    height: int | None = Field(default=None)
    size: int | None = Field(default=None)

class ModelImageMetadata(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    file_upload_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    keypoints: str | None = Field(default=None) #TODO: should be a json field

class FileUploadPipeline(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    file_upload_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    pipeline_id: uuid.UUID = Field(default_factory=uuid.uuid4)

class PipelineState(SQLModel, table=True):
    pipeline_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    state: int | None = Field(default=0)
    has_completed: bool | None = Field(default=False)
    has_error: bool | None = Field(default=False)
    error_message: str | None = Field(default=None)
    pipeline_parameters: str | None = Field(default=None, max_length=255)