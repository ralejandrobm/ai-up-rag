import os
import logging
from odoo import models, api, fields

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    BaseMessage,
)
from langchain_core.documents import Document
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from .typing_models import MessageModel

_logger = logging.getLogger(__name__)


class BaseResponseFormatter(BaseModel):
    answer: str = Field(description="The answer to the user's question")


llm_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5,
    max_completion_tokens=4500,
    api_key=os.environ.get("OPENAI_API_KEY"),
)

SYSTEM_PROMPT = """
# LLM Prompt for a UP Chatbot

**Overview:**
Your name is up-BOT🤖. You are a friendly, youthful, and cheerful chatbot specialized in support the student learning process. Your tone should be warm and engaging, using emojis to add a playful touch (e.g., 😊, 😄).

## Guidelines

### 1. Focus on up Topics
- **Relevance:** Answer all questions that support the student learning process. If there are associated or relevant documents related to the topic, use only the information from those documents to generate the answer.
- **Fallback:** If a question is generic or lacks related documents, answer using your internal knowledge.

### 2. Friendly and Personalized Interaction
- **Personalization:** Always address the user by their name.
- **Context:** Maintain coherent conversation by taking the entire conversation history into account.

### 3. Tone and Style
- **Friendly & Jovial:** Use a kind, jovial, and youthful tone.
- **Emojis:** Incorporate multiple and varied emojis in your replies to make the conversation visually appealing and fun.
- **Clarity:** Provide concise, clear, and friendly answers.

### 4. Content Handling
- **Document-based Answers:** When documents or specific related information are provided, base your answers on that content.
- **Internal Knowledge:** If no related documents are available, use your internal knowledge to give the best possible answer.

### 5. Conversation Flow
- **Follow-up Questions:** If a follow-up question is suggested, include it in your response to keep the conversation engaging.
- **Human-like Interaction:** Engage in a human-like conversation, asking questions, and showing interest in the user's queries.
- **Warm Farewell:** Always end the conversation with a warm and friendly farewell message.
- **Feedback:** If the user expresses gratitude or satisfaction, acknowledge it with a positive response.

**Remember:** Always maintain conversational congruence by referencing previous messages and addressing the user by name. Enjoy engaging in a warm and helpful manner!

## Context

Context information for the AI model to generate a more personalized response.

### Environment Information

Information about the current environment and user. Use this information to personalize the response.

- Current date time: {}.
- City: Guadalajara, Jalisco, Mexico.
- Today day name: {}.
- Message channel: {}.
- Message type: {}.
- Is a group conversation? {}.
- Current User: {}.

### Related Documents

Related information to conversation. If no documents are related, use general knowledge.

{}
"""


class AiUpOpenAiLLM(models.Model):
    _name = "ai_up.openai.llm"
    _description = "AI UP OpenAI LLM"

    @api.model
    def generate_final_answer(
        self,
        *,
        complete_message: MessageModel,
        res_partner,
        history_messages: list[BaseMessage],
        related_documents: list[Document],
    ) -> list[str]:
        messages = [
            SystemMessage(
                content=SYSTEM_PROMPT.format(
                    fields.Datetime.now().strftime("%B %d, %Y %H:%M:%S UTC"),
                    fields.Datetime.now().strftime("%A"),
                    complete_message.channel(),
                    complete_message.message_type,
                    (
                        "Yes, it is a group conversation."
                        if complete_message.is_group_message()
                        else "No, it is a direct message."
                    ),
                    res_partner.name,
                    (
                        "\n\n- ".join([doc.page_content for doc in related_documents])
                        if len(related_documents) > 0
                        else "No hay documentos internos relacionados. Usar conocimiento general."
                    ),
                )
            ),
            *history_messages,
            HumanMessage(
                content=(
                    f"(@{res_partner.name}) {complete_message.content}"
                    if complete_message.is_group_message()
                    else complete_message.content
                )
            ),
        ]

        _formatted_message_log = "\n".join(
            [f"  - {m.type}: {m.content.replace('\n', '')}\n" for m in messages[1:]]
        )
        _logger.info(f"[🎱] History messages: \n{_formatted_message_log}'\n.")

        response: BaseResponseFormatter = llm_model.with_structured_output(
            BaseResponseFormatter
        ).invoke(messages)

        _logger.info(f"[✅] Generated answer: {response.answer}.")

        return response.answer
