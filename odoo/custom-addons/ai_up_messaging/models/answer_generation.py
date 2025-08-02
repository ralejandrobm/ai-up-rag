import logging

from odoo import models, api

from langchain_core.documents import Document

from .typing_models import MessageModel


_logger = logging.getLogger(__name__)


class AiUpAnswerGeneration(models.Model):
    _name = "ai_up.answer.generation"
    _description = "AI UP Answer Generation"

    @api.model
    def generate_answer(
        self,
        *,
        complete_message: MessageModel,
    ) -> list[str]:
        _logger.info(
            f"[✅][] Generating answer for: [{complete_message.channel()}] {complete_message.author.username}: {complete_message.content}"
        )

        # TODO: Improve the process of generating the answer
        # 1. Generate a complete question to search
        # 2. Improve the search process
        # 3. Use RAG to generate the answer
        # 4. Format correctly the answer to be used in the chat

        res_partner = self.env["ai_up.message.history"].get_or_create_partner(
            partner={
                "name": complete_message.author.username,
                "mobile": complete_message.author.mobile,
            },
        )

        history_messages = self.env["ai_up.message.history"].get_messages(
            res_partner=res_partner,
            message=complete_message,
        )

        self.env["ai_up.message.history"].save_message(
            res_partner=res_partner,
            message=complete_message,
            is_message_from_partner=True,
        )

        related_documents: list[Document] = self.env[
            "ai_up.advertisement"
        ].similarity_search(
            query=complete_message.content,
        )

        answer = self.env["ai_up.openai.llm"].generate_final_answer(
            complete_message=complete_message,
            res_partner=res_partner,
            history_messages=history_messages,
            related_documents=related_documents,
        )

        self.env["ai_up.message.history"].save_message(
            res_partner=res_partner,
            message=MessageModel(
                content=answer,
                author=complete_message.author,
                message_type=complete_message.message_type,
                channel_type=complete_message.channel_type,
                channel_name=complete_message.channel_name,
            ),
            is_message_from_partner=False,
        )

        return [answer]
