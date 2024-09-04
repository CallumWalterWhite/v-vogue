import uuid
from sqlmodel import Field, Relationship, SQLModel

class MessageBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str | None = Field(default=None, max_length=255)
    message_type: str | None = Field(default=None, max_length=255)
    correlation_id: str | None = Field(default=None, max_length=255)


class OutboundMessage(MessageBase, table=True):
    is_sent: bool | None = Field(default=False)

class InboundMessage(MessageBase, table=True):
    is_success: bool | None = Field(default=None)