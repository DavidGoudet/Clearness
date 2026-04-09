import logging

from django.conf import settings
from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "Thank you for sharing. Your reflection matters."

_client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    timeout=settings.OPENAI_TIMEOUT,
    max_retries=settings.OPENAI_MAX_RETRIES,
)

SYSTEM_PROMPT_TEMPLATE = (
    "You are a warm, empathetic journaling companion. "
    "The user just completed a daily reflection and their current mood is '{mood}'. "
    "Respond with a brief, heartfelt acknowledgment (2-3 sentences) that: "
    "- Validates their feelings based on their mood\n"
    "- References something specific from what they shared\n"
    "- Ends with gentle encouragement\n"
    "Do not ask questions. Do not use bullet points or lists. "
    "Keep your tone conversational and caring."
)


def generate_acknowledgment(mood: str, reflection_text: str) -> str:
    """Generate a personalized acknowledgment using OpenAI.

    Args:
        mood: The user's selected mood (e.g. "happy", "down").
        reflection_text: The user's reflection journal entry.

    Returns:
        A personalized acknowledgment string, or FALLBACK_MESSAGE on failure.
    """
    try:
        response = _client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_TEMPLATE.format(mood=mood),
                },
                {
                    "role": "user",
                    "content": reflection_text,
                },
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except (OpenAIError, Exception) as exc:
        logger.error("OpenAI API error generating acknowledgment: %s", exc)
        return FALLBACK_MESSAGE
