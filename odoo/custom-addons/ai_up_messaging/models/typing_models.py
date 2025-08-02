from typing import Literal, Optional

from pydantic import BaseModel, Field


class AuthorModel(BaseModel):
    username: str = Field(..., min_length=1)
    mobile: Optional[str] = Field(
        ...,
    )


class MessageModel(BaseModel):
    author: AuthorModel = Field(...)
    content: str = Field(..., min_length=1)
    message_type: Literal["direct_message", "channel_command", "channel_mention"] = (
        Field(...)
    )
    channel_type: Literal["discord", "whatsapp"] = Field(
        ..., description="The type of channel."
    )
    channel_name: Optional[str] = Field(..., description="The name of the channel.")

    def channel(self):
        if not self.is_group_message():
            return self.channel_type

        return f"{self.channel_type}.{self.channel_name}"

    def message_from(self):
        message_type = (
            "channel_message" if self.is_group_message() else "direct_message"
        )

        return f"{self.channel()}:{message_type}"

    def is_group_message(self):
        return self.message_type != "direct_message"
