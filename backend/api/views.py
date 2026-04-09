import logging
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.db import transaction
from django.db.models import Count, Max
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import verify_apple_token, verify_google_token
from .models import ChatMessage, DailyChat, Item, User
from .serializers import (
    AppleAuthSerializer,
    DailyChatSerializer,
    DailyChatUpdateSerializer,
    GoogleAuthSerializer,
    ItemSerializer,
    LogoutSerializer,
    MonthlyChatSerializer,
    ProfileStatsSerializer,
    UserSerializer,
)
from .services import get_or_create_today_chat, get_reflection_prompt_content, submit_reflection

logger = logging.getLogger(__name__)


class ItemViewSet(viewsets.ModelViewSet):
    """CRUD API for Items."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [AllowAny]


class GoogleAuthView(APIView):
    """Authenticate a user via Google OAuth2 ID token.

    POST /api/auth/google/
    Body: {"id_token": "<google-id-token>"}
    Returns: {"access": "...", "refresh": "...", "user": {...}}
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data["id_token"]

        try:
            google_info = verify_google_token(token)
        except ValueError:
            logger.warning("Invalid Google token received")
            return Response(
                {"detail": "Invalid Google token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user, created = User.objects.get_or_create(
            auth_provider="google",
            auth_provider_id=google_info["provider_id"],
            defaults={
                "email": google_info["email"],
                "display_name": google_info["name"] or google_info["email"],
            },
        )

        if created:
            user.set_unusable_password()
            user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class AppleAuthView(APIView):
    """Authenticate a user via Apple Sign-In identity token.

    POST /api/auth/apple/
    Body: {"identity_token": "<apple-identity-token>", "user_name": "optional name"}
    Returns: {"access": "...", "refresh": "...", "user": {...}}
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AppleAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        identity_token = serializer.validated_data["identity_token"]
        user_name = serializer.validated_data.get("user_name", "")

        try:
            apple_info = verify_apple_token(identity_token)
        except ValueError:
            logger.warning("Invalid Apple token received")
            return Response(
                {"detail": "Invalid Apple token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email = apple_info["email"]
        # Apple only sends name on first sign-in; use provided name or fall back to email prefix
        display_name = user_name or email.split("@")[0] if email else "User"

        user, created = User.objects.get_or_create(
            auth_provider="apple",
            auth_provider_id=apple_info["provider_id"],
            defaults={
                "email": email,
                "display_name": display_name,
            },
        )

        if created:
            user.set_unusable_password()
            user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """Blacklist the refresh token to invalidate the session server-side.

    POST /api/auth/logout/
    Body: {"refresh": "<refresh-token>"}
    Requires: Bearer token in Authorization header.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or already blacklisted token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_200_OK)


class ProfileView(APIView):
    """Retrieve the authenticated user's profile.

    GET /api/me/
    Requires: Bearer token in Authorization header.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileStatsView(APIView):
    """Retrieve computed journey stats for the authenticated user.

    GET /api/profile/stats/
    Requires: Bearer token in Authorization header.
    Returns: {total_chats, current_streak, longest_streak, most_frequent_mood}
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        completed_chats = DailyChat.objects.filter(
            user=user, status=DailyChat.StatusChoice.COMPLETED
        )

        total_chats = completed_chats.count()

        # Get all completed chat dates ordered ascending
        chat_dates = list(
            completed_chats.order_by("date").values_list("date", flat=True)
        )

        current_streak = self._compute_current_streak(chat_dates, user)
        longest_streak = self._compute_longest_streak(chat_dates)
        most_frequent_mood = self._compute_most_frequent_mood(completed_chats)

        data = {
            "total_chats": total_chats,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "most_frequent_mood": most_frequent_mood,
        }
        serializer = ProfileStatsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _compute_current_streak(self, chat_dates, user):
        if not chat_dates:
            return 0

        user_tz = ZoneInfo(user.timezone)
        today = timezone.now().astimezone(user_tz).date()

        # Start from today or yesterday
        last_date = chat_dates[-1]
        if last_date == today:
            streak_date = today
        elif last_date == today - timedelta(days=1):
            streak_date = today - timedelta(days=1)
        else:
            return 0

        date_set = set(chat_dates)
        streak = 0
        while streak_date in date_set:
            streak += 1
            streak_date -= timedelta(days=1)

        return streak

    def _compute_longest_streak(self, chat_dates):
        if not chat_dates:
            return 0

        longest = 1
        current = 1
        for i in range(1, len(chat_dates)):
            if chat_dates[i] == chat_dates[i - 1] + timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1

        return longest

    def _compute_most_frequent_mood(self, completed_chats):
        result = (
            completed_chats.exclude(mood="")
            .values("mood")
            .annotate(count=Count("mood"))
            .order_by("-count")
            .first()
        )

        if not result:
            return None

        mood_value = result["mood"]
        display = DailyChat.MOOD_DISPLAY.get(mood_value, mood_value)
        # Parse emoji from display string like "Happy 😊"
        parts = display.rsplit(" ", 1)
        label = parts[0] if len(parts) == 2 else mood_value.capitalize()
        emoji = parts[1] if len(parts) == 2 else ""

        return {"value": mood_value, "emoji": emoji, "label": label}


class TodayChatView(APIView):
    """Get or create the daily chat for a given date.

    GET /api/chats/today/?date=YYYY-MM-DD
    Requires: Bearer token in Authorization header.
    Returns: DailyChat with all messages.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"detail": "date query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            chat = get_or_create_today_chat(request.user, date_str)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DailyChatSerializer(chat)
        return Response(serializer.data)


class DailyChatDetailView(APIView):
    """Retrieve or update a specific daily chat.

    GET  /api/chats/<pk>/  →  Full DailyChat with messages.
    PATCH /api/chats/<pk>/
    Body: {"mood": "happy"} OR {"user_response": "..."}
    Requires: Bearer token in Authorization header.
    Returns: Full DailyChat with messages.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            chat = DailyChat.objects.prefetch_related("messages").get(
                pk=pk, user=request.user
            )
        except DailyChat.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(DailyChatSerializer(chat).data)

    def patch(self, request, pk):
        try:
            chat = DailyChat.objects.get(pk=pk, user=request.user)
        except DailyChat.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if chat.status == DailyChat.StatusChoice.COMPLETED:
            return Response(
                {"detail": "This chat is completed and cannot be modified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DailyChatUpdateSerializer(instance=chat, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if "mood" in serializer.validated_data:
            chat = self._handle_mood(chat, serializer.validated_data["mood"])
        else:
            chat = self._handle_reflection(chat, serializer.validated_data["user_response"])

        return Response(DailyChatSerializer(chat).data)

    def _handle_mood(self, chat, mood):
        with transaction.atomic():
            chat.mood = mood
            chat.save(update_fields=["mood"])
            max_order = (
                chat.messages.aggregate(max_order=Max("order"))["max_order"] or 0
            )
            ChatMessage.objects.bulk_create([
                ChatMessage(
                    daily_chat=chat,
                    sender=ChatMessage.SenderChoice.USER,
                    message_type=ChatMessage.MessageType.MOOD_RESPONSE,
                    content=DailyChat.MOOD_DISPLAY[mood],
                    order=max_order + 1,
                ),
                ChatMessage(
                    daily_chat=chat,
                    sender=ChatMessage.SenderChoice.BOT,
                    message_type=ChatMessage.MessageType.REFLECTION_PROMPT,
                    content=get_reflection_prompt_content(),
                    order=max_order + 2,
                ),
            ])
        return DailyChat.objects.prefetch_related("messages").get(pk=chat.pk)

    def _handle_reflection(self, chat, user_response_text):
        return submit_reflection(chat, user_response_text)


class MonthlyChatListView(APIView):
    """List completed chats for a given month.

    GET /api/chats/monthly/?year=YYYY&month=MM
    Requires: Bearer token in Authorization header.
    Returns: List of {id, date, mood} for completed chats in the specified month.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        year_str = request.query_params.get("year")
        month_str = request.query_params.get("month")

        if not year_str or not month_str:
            return Response(
                {"detail": "year and month query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            year = int(year_str)
            month = int(month_str)
            if month < 1 or month > 12:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"detail": "year and month must be valid integers (month 1-12)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chats = DailyChat.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month,
            status=DailyChat.StatusChoice.COMPLETED,
        ).order_by("date")

        serializer = MonthlyChatSerializer(chats, many=True)
        return Response(serializer.data)
