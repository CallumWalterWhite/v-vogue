from sqlmodel import Field, Relationship, SQLModel

class MessageBase(SQLModel):
    content: str | None = Field(default=None, max_length=255)
    message_type: str | None = Field(default=None, max_length=255)


class OutboundMessageBase(MessageBase):
    is_sent: bool | None = Field(default=None)

class OutboundMessageBase(MessageBase):
    is_success: bool | None = Field(default=None)