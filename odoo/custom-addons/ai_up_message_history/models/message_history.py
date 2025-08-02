import logging
import re

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

from odoo import models, api

from ...ai_up_messaging.models.typing_models import MessageModel


_logger = logging.getLogger(__name__)


class AiUpMessageHistory(models.Model):
    _name = "ai_up.message.history"
    _description = "AI UP Message History"

    @api.model
    def save_message(
        self,
        *,
        res_partner,
        message: MessageModel,
        is_message_from_partner: bool,
    ):
        author_id = res_partner.id if is_message_from_partner else 1

        mail_message = self.env["mail.message"].create(
            {
                "author_id": author_id,
                "model": "ai_up.message.history",
                "res_id": res_partner.id,
                "message_type": "comment",
                "body": message.content,
                "email_from": f'"{res_partner.name}" <{message.message_from()}>',
                "subtype_id": self.env.ref("mail.mt_comment").id,
            }
        )

        return mail_message

    @api.model
    def get_messages(
        self,
        *,
        res_partner,
        message: MessageModel,
    ) -> list[BaseMessage]:
        domain = [("model", "=", "ai_up.message.history")]

        domain.append(
            (
                "email_from",
                "like",
                f"<{message.message_from()}>%",
            )
        )
        if not message.is_group_message():
            domain.append(("res_id", "=", res_partner.id))

        messages = self.env["mail.message"].search(domain, order="id desc", limit=20)
        messages = messages.sorted(key=lambda r: r.id)

        return [
            (
                AIMessage(content=self._clean_message_body(msg.body))
                if msg.author_id.id == 1
                else HumanMessage(
                    content=self._format_human_message(
                        message=msg.body,
                        email_from=msg.email_from,
                    )
                )
            )
            for msg in messages
        ]

    def _format_human_message(
        self,
        *,
        message: str,
        email_from: str,
    ) -> str:
        clean_message = self._clean_message_body(message)

        if "direct_message" in email_from:
            return clean_message

        username = re.search(r"\"(.+?)\"", email_from).group(1)
        if not username:
            return clean_message

        return f"(@{username}) {clean_message}"

    def _clean_message_body(
        self,
        message: str,
    ) -> str:
        return re.sub(r"<[^>]+>", "", message)

    @api.model
    def get_or_create_partner(
        self,
        *,
        partner: dict[str, str],
    ) -> list[str]:
        _logger.info(f"[✅][] Get or create partner: {partner}")

        res_partner = self.env["res.partner"].search(
            [
                ("name", "=", partner["name"]),
                ("mobile", "=", partner["mobile"]),
            ]
        )

        if res_partner:
            return res_partner

        res_partner = self.env["res.partner"].create(
            {
                "name": partner["name"],
                "mobile": partner["mobile"],
            }
        )
        return res_partner
