from odoo import http
from odoo.http import Response

import json
import logging
from typing import Literal, Optional
from pydantic import BaseModel, ValidationError, Field

from ..models.typing_models import MessageModel, AuthorModel

_logger = logging.getLogger(__name__)


class AuthorMessageRequestModel(BaseModel):
    id: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)


class MessageRequestModel(BaseModel):
    author: AuthorMessageRequestModel = Field(...)
    message: str = Field(..., min_length=1)
    message_type: Literal["direct_message", "channel_command", "channel_mention"] = (
        Field(...)
    )
    channel_name: Optional[str] = Field(..., description="The name of the channel.")


class AiUpDiscordAnswerConnectorController(http.Controller):
    @http.route(
        "/api/v1/discord/answers",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def get_answers(self, **kwargs):
        """
        Get AI generated answers
        """

        # TODO: add authentication
        # TODO: add error handling
        # TODO: add logging
        # TODO: add discord message creation

        try:
            body = json.loads(http.request.httprequest.data)
            message_request = MessageRequestModel(**body)
        except ValidationError as e:
            _logger.error(f"[❌][AiUpMessagingController] Error: {e.json()}")
            return Response(
                json.dumps({"status": 400, "error": json.loads(e.json())}),
                mimetype="application/json",
                status=400,
            )

        # TODO: improve permission handling. Should not use sudo!
        answer = (
            http.request.env["ai_up.answer.generation"]
            .sudo()
            .generate_answer(
                complete_message=MessageModel(
                    author=AuthorModel(
                        username=message_request.author.username,
                        mobile=None,
                    ),
                    content=message_request.message,
                    message_type=message_request.message_type,
                    channel_type="discord",
                    channel_name=message_request.channel_name,
                )
            )
        )

        return Response(
            json.dumps({"status": 200, "data": answer}),
            mimetype="application/json",
            status=200,
        )
