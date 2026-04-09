import logging
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from django.db.models import Max
from django.utils import timezone

from ..models import ChatMessage, DailyChat
from . import llm_service

logger = logging.getLogger(__name__)


def get_reflection_prompt_content() -> str:
    return (
        "Take a moment to share what's on your mind. "
        "There are no right or wrong answers — just write whatever feels true for you."
    )


def submit_reflection(chat: DailyChat, user_response_text: str) -> DailyChat:
    """Create reflection_response + acknowledgment messages and complete the chat."""
    acknowledgment_content = llm_service.generate_acknowledgment(
        chat.mood, user_response_text
    )

    max_order = chat.messages.aggregate(max_order=Max("order"))["max_order"] or 0

    with transaction.atomic():
        ChatMessage.objects.bulk_create([
            ChatMessage(
                daily_chat=chat,
                sender=ChatMessage.SenderChoice.USER,
                message_type=ChatMessage.MessageType.REFLECTION_RESPONSE,
                content=user_response_text,
                order=max_order + 1,
            ),
            ChatMessage(
                daily_chat=chat,
                sender=ChatMessage.SenderChoice.BOT,
                message_type=ChatMessage.MessageType.ACKNOWLEDGMENT,
                content=acknowledgment_content,
                order=max_order + 2,
            ),
        ])
        chat.status = DailyChat.StatusChoice.COMPLETED
        chat.completed_at = timezone.now()
        chat.save(update_fields=["status", "completed_at"])

    return (
        DailyChat.objects.filter(pk=chat.pk)
        .prefetch_related("messages")
        .first()
    )


def _get_time_of_day_period(user_hour: int) -> str:
    """Return the time-of-day period based on the user's local hour.

    morning:   05:00 - 11:59
    afternoon: 12:00 - 16:59
    evening:   17:00 - 04:59
    """
    if 5 <= user_hour <= 11:
        return "morning"
    elif 12 <= user_hour <= 16:
        return "afternoon"
    else:
        return "evening"


def get_or_create_today_chat(user, local_date_str: str) -> DailyChat:
    """Return the user's DailyChat for the given local date, creating one if needed.

    Args:
        user: The authenticated User instance.
        local_date_str: Date string in YYYY-MM-DD format from the client.

    Returns:
        DailyChat instance with prefetched messages.

    Raises:
        ValueError: If the date format is invalid or the date is unreasonable.
    """
    # Parse the date string
    try:
        local_date = date.fromisoformat(local_date_str)
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"Invalid date format: '{local_date_str}'. Expected YYYY-MM-DD."
        ) from exc

    # Validate the date is within +/- 1 day of server-calculated user date
    user_tz = ZoneInfo(user.timezone)
    server_user_date = datetime.now(tz=user_tz).date()
    delta = abs((local_date - server_user_date).days)
    if delta > 1:
        raise ValueError(
            f"Date '{local_date_str}' is too far from the current date "
            f"in your timezone ({user.timezone})."
        )

    # AC3, AC5: Return existing chat if one exists for this user + date
    existing = (
        DailyChat.objects.filter(user=user, date=local_date)
        .prefetch_related("messages")
        .first()
    )
    if existing:
        return existing

    # Determine time-of-day for the greeting
    user_now = datetime.now(tz=user_tz)
    period = _get_time_of_day_period(user_now.hour)

    # Build greeting messages
    greeting_content = (
        f"Good {period}, {user.display_name}! "
        f"How are you feeling today?"
    )
    mood_prompt_content = (
        "Take a moment to check in with yourself. "
        "How are you feeling right now?"
    )

    try:
        with transaction.atomic():
            chat = DailyChat.objects.create(user=user, date=local_date)
            ChatMessage.objects.bulk_create(
                [
                    ChatMessage(
                        daily_chat=chat,
                        sender=ChatMessage.SenderChoice.BOT,
                        message_type=ChatMessage.MessageType.GREETING,
                        content=greeting_content,
                        order=0,
                    ),
                    ChatMessage(
                        daily_chat=chat,
                        sender=ChatMessage.SenderChoice.BOT,
                        message_type=ChatMessage.MessageType.MOOD_PROMPT,
                        content=mood_prompt_content,
                        order=1,
                    ),
                ]
            )
    except IntegrityError:
        # Race condition: another request created the chat concurrently
        logger.info(
            "Race condition handled: chat already exists for user=%s date=%s",
            user.id,
            local_date,
        )
        chat = (
            DailyChat.objects.filter(user=user, date=local_date)
            .prefetch_related("messages")
            .first()
        )
        if chat is None:
            raise  # pragma: no cover — should not happen
        return chat

    # Reload with prefetched messages for consistent serialization
    return (
        DailyChat.objects.filter(pk=chat.pk)
        .prefetch_related("messages")
        .first()
    )
