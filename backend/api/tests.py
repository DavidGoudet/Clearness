from datetime import date, datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ChatMessage, DailyChat, Item, User


class ItemModelTest(TestCase):
    def test_str_representation(self):
        item = Item(name="Test Item")
        self.assertEqual(str(item), "Test Item")


class ItemAPITest(APITestCase):
    def test_list_items(self):
        response = self.client.get("/api/items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_item(self):
        data = {"name": "New Item", "description": "A test item"}
        response = self.client.post("/api/items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(Item.objects.first().name, "New Item")


class UserModelTest(TestCase):
    def test_str_representation(self):
        user = User(display_name="Alice")
        self.assertEqual(str(user), "Alice")

    def test_user_unique_constraint(self):
        """Duplicate auth_provider + auth_provider_id raises IntegrityError."""
        User.objects.create_user(
            email="alice@example.com",
            password=None,
            display_name="Alice",
            auth_provider="google",
            auth_provider_id="google-123",
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="alice2@example.com",
                password=None,
                display_name="Alice Duplicate",
                auth_provider="google",
                auth_provider_id="google-123",
            )


class GoogleAuthTest(APITestCase):
    """Tests for the POST /api/auth/google/ endpoint."""

    GOOGLE_AUTH_URL = "/api/auth/google/"

    MOCK_GOOGLE_INFO = {
        "email": "testuser@gmail.com",
        "name": "Test User",
        "provider_id": "google-sub-12345",
    }

    @patch("api.views.verify_google_token")
    def test_google_auth_new_user(self, mock_verify):
        """A valid token for a new user creates the user and returns JWTs."""
        mock_verify.return_value = self.MOCK_GOOGLE_INFO

        response = self.client.post(
            self.GOOGLE_AUTH_URL, {"id_token": "valid-token"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "testuser@gmail.com")
        self.assertEqual(response.data["user"]["display_name"], "Test User")
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.first()
        self.assertEqual(user.auth_provider, "google")
        self.assertEqual(user.auth_provider_id, "google-sub-12345")
        self.assertFalse(user.has_usable_password())

    @patch("api.views.verify_google_token")
    def test_google_auth_existing_user(self, mock_verify):
        """A valid token for an existing user returns JWTs without creating a duplicate."""
        mock_verify.return_value = self.MOCK_GOOGLE_INFO

        User.objects.create_user(
            email="testuser@gmail.com",
            password=None,
            display_name="Test User",
            auth_provider="google",
            auth_provider_id="google-sub-12345",
        )
        self.assertEqual(User.objects.count(), 1)

        response = self.client.post(
            self.GOOGLE_AUTH_URL, {"id_token": "valid-token"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(User.objects.count(), 1)

    @patch("api.views.verify_google_token")
    def test_google_auth_invalid_token(self, mock_verify):
        """An invalid token returns 401."""
        mock_verify.side_effect = ValueError("Invalid token")

        response = self.client.post(
            self.GOOGLE_AUTH_URL, {"id_token": "invalid-token"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid Google token.")
        self.assertEqual(User.objects.count(), 0)

    def test_google_auth_missing_token(self):
        """A request with no id_token returns 400."""
        response = self.client.post(self.GOOGLE_AUTH_URL, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("id_token", response.data)


class AppleAuthTest(APITestCase):
    """Tests for the POST /api/auth/apple/ endpoint."""

    APPLE_AUTH_URL = "/api/auth/apple/"

    MOCK_APPLE_INFO = {
        "email": "testuser@privaterelay.appleid.com",
        "provider_id": "apple-sub-67890",
    }

    @patch("api.views.verify_apple_token")
    def test_apple_auth_new_user(self, mock_verify):
        """AC1: A valid token for a new user creates the user and returns JWTs."""
        mock_verify.return_value = self.MOCK_APPLE_INFO

        response = self.client.post(
            self.APPLE_AUTH_URL,
            {"identity_token": "valid-apple-token", "user_name": "Jane Appleseed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(
            response.data["user"]["email"], "testuser@privaterelay.appleid.com"
        )
        self.assertEqual(response.data["user"]["display_name"], "Jane Appleseed")
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.first()
        self.assertEqual(user.auth_provider, "apple")
        self.assertEqual(user.auth_provider_id, "apple-sub-67890")
        self.assertFalse(user.has_usable_password())

    @patch("api.views.verify_apple_token")
    def test_apple_auth_existing_user(self, mock_verify):
        """AC2: A valid token for an existing user returns JWTs without creating a duplicate."""
        mock_verify.return_value = self.MOCK_APPLE_INFO

        User.objects.create_user(
            email="testuser@privaterelay.appleid.com",
            password=None,
            display_name="Jane Appleseed",
            auth_provider="apple",
            auth_provider_id="apple-sub-67890",
        )
        self.assertEqual(User.objects.count(), 1)

        response = self.client.post(
            self.APPLE_AUTH_URL,
            {"identity_token": "valid-apple-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertEqual(User.objects.count(), 1)

    @patch("api.views.verify_apple_token")
    def test_apple_auth_hide_my_email(self, mock_verify):
        """AC3: Relay email from 'Hide My Email' is stored correctly."""
        mock_verify.return_value = {
            "email": "abc123@privaterelay.appleid.com",
            "provider_id": "apple-sub-relay",
        }

        response = self.client.post(
            self.APPLE_AUTH_URL,
            {"identity_token": "valid-token", "user_name": "Private User"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.first()
        self.assertEqual(user.email, "abc123@privaterelay.appleid.com")
        self.assertEqual(user.display_name, "Private User")

    @patch("api.views.verify_apple_token")
    def test_apple_auth_invalid_token(self, mock_verify):
        """AC4: An invalid token returns 401."""
        mock_verify.side_effect = ValueError("Invalid token")

        response = self.client.post(
            self.APPLE_AUTH_URL,
            {"identity_token": "invalid-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid Apple token.")
        self.assertEqual(User.objects.count(), 0)

    def test_apple_auth_missing_token(self):
        """A request with no identity_token returns 400."""
        response = self.client.post(self.APPLE_AUTH_URL, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("identity_token", response.data)

    @patch("api.views.verify_apple_token")
    def test_apple_auth_no_name_provided(self, mock_verify):
        """When no user_name is provided, display_name falls back to email prefix."""
        mock_verify.return_value = {
            "email": "janedoe@icloud.com",
            "provider_id": "apple-sub-noname",
        }

        response = self.client.post(
            self.APPLE_AUTH_URL,
            {"identity_token": "valid-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.first()
        self.assertEqual(user.display_name, "janedoe")


class ProfileTest(APITestCase):
    """Tests for the GET /api/me/ endpoint."""

    PROFILE_URL = "/api/me/"

    def setUp(self):
        self.user = User.objects.create_user(
            email="profile@example.com",
            password=None,
            display_name="Profile User",
            auth_provider="google",
            auth_provider_id="google-profile-1",
            avatar_emoji="\U0001f60a",
            timezone="America/New_York",
        )

    def test_profile_authenticated(self):
        """An authenticated user can retrieve their profile."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        response = self.client.get(self.PROFILE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "profile@example.com")
        self.assertEqual(response.data["display_name"], "Profile User")
        self.assertEqual(response.data["timezone"], "America/New_York")

    def test_profile_unauthenticated(self):
        """An unauthenticated request to /me/ returns 401."""
        response = self.client.get(self.PROFILE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTest(APITestCase):
    """Tests for the POST /api/auth/refresh/ endpoint."""

    REFRESH_URL = "/api/auth/refresh/"

    def setUp(self):
        self.user = User.objects.create_user(
            email="refresh@example.com",
            password=None,
            display_name="Refresh User",
            auth_provider="google",
            auth_provider_id="google-refresh-1",
        )

    def test_token_refresh(self):
        """A valid refresh token returns a new access token."""
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            self.REFRESH_URL, {"refresh": str(refresh)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class LogoutTest(APITestCase):
    """Tests for the POST /api/auth/logout/ endpoint."""

    LOGOUT_URL = "/api/auth/logout/"
    REFRESH_URL = "/api/auth/refresh/"

    def setUp(self):
        self.user = User.objects.create_user(
            email="logout@example.com",
            password=None,
            display_name="Logout User",
            auth_provider="google",
            auth_provider_id="google-logout-1",
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(self.refresh.access_token)}"
        )

    def test_logout_blacklists_token(self):
        """Logout returns 200 and the refresh token is blacklisted."""
        response = self.client.post(
            self.LOGOUT_URL, {"refresh": str(self.refresh)}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_blacklisted_token_cannot_refresh(self):
        """A blacklisted refresh token cannot be used to get a new access token."""
        self.client.post(
            self.LOGOUT_URL, {"refresh": str(self.refresh)}, format="json"
        )

        self.client.credentials()  # Clear auth header
        response = self.client.post(
            self.REFRESH_URL, {"refresh": str(self.refresh)}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_unauthenticated(self):
        """Logout without a valid access token returns 401."""
        self.client.credentials()  # Clear auth header
        response = self.client.post(
            self.LOGOUT_URL, {"refresh": str(self.refresh)}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_missing_refresh_token(self):
        """Logout without a refresh token in the body returns 400."""
        response = self.client.post(self.LOGOUT_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DailyChatModelTest(TestCase):
    """Tests for the DailyChat model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="chat@example.com",
            password=None,
            display_name="Chat User",
            auth_provider="google",
            auth_provider_id="google-chat-1",
            timezone="America/New_York",
        )

    def test_daily_chat_model_str(self):
        """DailyChat __str__ returns 'display_name - date'."""
        chat = DailyChat.objects.create(
            user=self.user, date=date(2026, 3, 3)
        )
        self.assertEqual(str(chat), "Chat User \u2014 2026-03-03")

    def test_one_chat_per_user_per_day_constraint(self):
        """AC5: Creating two chats for the same user and date raises IntegrityError."""
        DailyChat.objects.create(user=self.user, date=date(2026, 3, 3))
        with self.assertRaises(IntegrityError):
            DailyChat.objects.create(user=self.user, date=date(2026, 3, 3))


class ChatMessageModelTest(TestCase):
    """Tests for the ChatMessage model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="msg@example.com",
            password=None,
            display_name="Msg User",
            auth_provider="google",
            auth_provider_id="google-msg-1",
            timezone="UTC",
        )
        self.chat = DailyChat.objects.create(
            user=self.user, date=date(2026, 3, 3)
        )

    def test_chat_message_model_str(self):
        """ChatMessage __str__ shows sender, type, and truncated content."""
        msg = ChatMessage.objects.create(
            daily_chat=self.chat,
            sender=ChatMessage.SenderChoice.BOT,
            message_type=ChatMessage.MessageType.GREETING,
            content="Good morning, Msg User! How are you feeling today?",
            order=0,
        )
        result = str(msg)
        self.assertIn("Bot", result)
        self.assertIn("greeting", result)
        self.assertIn("Good morning", result)


class TodayChatAPITest(APITestCase):
    """Tests for the GET /api/chats/today/ endpoint."""

    CHAT_URL = "/api/chats/today/"

    def setUp(self):
        self.user = User.objects.create_user(
            email="daily@example.com",
            password=None,
            display_name="Daily User",
            auth_provider="google",
            auth_provider_id="google-daily-1",
            timezone="America/New_York",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

    def _get_today_str(self):
        """Return today's date in the user's timezone as YYYY-MM-DD."""
        tz = ZoneInfo(self.user.timezone)
        return datetime.now(tz=tz).strftime("%Y-%m-%d")

    def test_today_chat_creates_new(self):
        """AC1, AC4: GET creates a new chat with greeting and mood prompt."""
        today = self._get_today_str()
        response = self.client.get(f"{self.CHAT_URL}?date={today}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["date"], today)
        self.assertEqual(response.data["status"], "in_progress")
        self.assertEqual(len(response.data["messages"]), 2)
        self.assertEqual(DailyChat.objects.count(), 1)

    def test_today_chat_returns_existing(self):
        """AC3, AC5: A second GET returns the same chat, not a duplicate."""
        today = self._get_today_str()
        response1 = self.client.get(f"{self.CHAT_URL}?date={today}")
        response2 = self.client.get(f"{self.CHAT_URL}?date={today}")

        self.assertEqual(response1.data["id"], response2.data["id"])
        self.assertEqual(DailyChat.objects.count(), 1)

    @patch("api.services.datetime")
    def test_today_chat_greeting_morning(self, mock_dt):
        """Greeting says 'Good morning' when user's local time is 9:00 AM."""
        tz = ZoneInfo("America/New_York")
        mock_now = datetime(2026, 3, 3, 9, 0, 0, tzinfo=tz)
        mock_dt.now.return_value = mock_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)

        response = self.client.get(f"{self.CHAT_URL}?date=2026-03-03")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        greeting = response.data["messages"][0]["content"]
        self.assertIn("Good morning", greeting)

    @patch("api.services.datetime")
    def test_today_chat_greeting_afternoon(self, mock_dt):
        """Greeting says 'Good afternoon' when user's local time is 2:00 PM."""
        tz = ZoneInfo("America/New_York")
        mock_now = datetime(2026, 3, 3, 14, 0, 0, tzinfo=tz)
        mock_dt.now.return_value = mock_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)

        response = self.client.get(f"{self.CHAT_URL}?date=2026-03-03")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        greeting = response.data["messages"][0]["content"]
        self.assertIn("Good afternoon", greeting)

    @patch("api.services.datetime")
    def test_today_chat_greeting_evening(self, mock_dt):
        """Greeting says 'Good evening' when user's local time is 8:00 PM."""
        tz = ZoneInfo("America/New_York")
        mock_now = datetime(2026, 3, 3, 20, 0, 0, tzinfo=tz)
        mock_dt.now.return_value = mock_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)

        response = self.client.get(f"{self.CHAT_URL}?date=2026-03-03")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        greeting = response.data["messages"][0]["content"]
        self.assertIn("Good evening", greeting)

    def test_today_chat_greeting_contains_display_name(self):
        """AC4: The greeting includes the user's display name."""
        today = self._get_today_str()
        response = self.client.get(f"{self.CHAT_URL}?date={today}")

        greeting = response.data["messages"][0]["content"]
        self.assertIn("Daily User", greeting)

    def test_today_chat_messages_structure(self):
        """Chat has 2 bot messages at order 0 (greeting) and 1 (mood_prompt)."""
        today = self._get_today_str()
        response = self.client.get(f"{self.CHAT_URL}?date={today}")

        messages = response.data["messages"]
        self.assertEqual(len(messages), 2)

        self.assertEqual(messages[0]["order"], 0)
        self.assertEqual(messages[0]["sender"], "bot")
        self.assertEqual(messages[0]["message_type"], "greeting")

        self.assertEqual(messages[1]["order"], 1)
        self.assertEqual(messages[1]["sender"], "bot")
        self.assertEqual(messages[1]["message_type"], "mood_prompt")

    def test_today_chat_unauthenticated(self):
        """Unauthenticated request returns 401."""
        self.client.credentials()
        response = self.client.get(f"{self.CHAT_URL}?date=2026-03-03")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_today_chat_missing_date_param(self):
        """Request without date query parameter returns 400."""
        response = self.client.get(self.CHAT_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date query parameter is required", response.data["detail"])

    def test_today_chat_invalid_date_format(self):
        """Request with invalid date format returns 400."""
        response = self.client.get(f"{self.CHAT_URL}?date=not-a-date")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid date format", response.data["detail"])

    def test_today_chat_date_validation(self):
        """Date too far from today returns 400."""
        response = self.client.get(f"{self.CHAT_URL}?date=2020-01-01")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("too far from the current date", response.data["detail"])


class MoodSelectionAPITest(APITestCase):
    """Tests for the PATCH /api/chats/<pk>/ endpoint — mood selection."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="mood@example.com",
            password=None,
            display_name="Mood User",
            auth_provider="google",
            auth_provider_id="google-mood-1",
            timezone="America/New_York",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
        self.chat = DailyChat.objects.create(
            user=self.user, date=date(2026, 3, 3)
        )
        # Seed with greeting + mood_prompt (order 0 and 1)
        ChatMessage.objects.create(
            daily_chat=self.chat,
            sender=ChatMessage.SenderChoice.BOT,
            message_type=ChatMessage.MessageType.GREETING,
            content="Good morning, Mood User!",
            order=0,
        )
        ChatMessage.objects.create(
            daily_chat=self.chat,
            sender=ChatMessage.SenderChoice.BOT,
            message_type=ChatMessage.MessageType.MOOD_PROMPT,
            content="How are you feeling today?",
            order=1,
        )

    def _url(self, pk=None):
        return f"/api/chats/{pk or self.chat.pk}/"

    def test_patch_mood_success(self):
        """AC3: PATCH returns 200, mood saved, status stays in_progress."""
        response = self.client.patch(
            self._url(), {"mood": "happy"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mood"], "happy")
        self.assertEqual(response.data["status"], "in_progress")
        self.chat.refresh_from_db()
        self.assertEqual(self.chat.mood, "happy")

    def test_patch_mood_creates_response_message(self):
        """AC2: Response includes mood_response message with sender=user."""
        response = self.client.patch(
            self._url(), {"mood": "calm"}, format="json"
        )
        messages = response.data["messages"]
        mood_msgs = [m for m in messages if m["message_type"] == "mood_response"]
        self.assertEqual(len(mood_msgs), 1)
        self.assertEqual(mood_msgs[0]["sender"], "user")
        self.assertEqual(mood_msgs[0]["content"], "Calm 😌")
        self.assertEqual(mood_msgs[0]["order"], 2)

    def test_patch_mood_all_five_values(self):
        """AC5: All 5 mood values save correctly."""
        moods = ["happy", "calm", "neutral", "down", "frustrated"]
        for mood_val in moods:
            # Create a fresh chat for each mood
            chat = DailyChat.objects.create(
                user=self.user, date=date(2026, 4, 1 + moods.index(mood_val))
            )
            ChatMessage.objects.create(
                daily_chat=chat,
                sender=ChatMessage.SenderChoice.BOT,
                message_type=ChatMessage.MessageType.GREETING,
                content="Hello!",
                order=0,
            )
            response = self.client.patch(
                self._url(chat.pk), {"mood": mood_val}, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["mood"], mood_val)

    def test_patch_mood_already_set_returns_400(self):
        """AC4: Second PATCH rejected when mood already set."""
        self.client.patch(self._url(), {"mood": "happy"}, format="json")
        response = self.client.patch(
            self._url(), {"mood": "calm"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_mood_invalid_value_returns_400(self):
        """Invalid mood value is rejected."""
        response = self.client.patch(
            self._url(), {"mood": "ecstatic"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_mood_empty_string_returns_400(self):
        """Empty mood string is rejected."""
        response = self.client.patch(
            self._url(), {"mood": ""}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_chat_not_owned_returns_404(self):
        """User A cannot PATCH user B's chat."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password=None,
            display_name="Other",
            auth_provider="google",
            auth_provider_id="google-other-1",
        )
        other_chat = DailyChat.objects.create(
            user=other_user, date=date(2026, 3, 3)
        )
        response = self.client.patch(
            self._url(other_chat.pk), {"mood": "happy"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_unauthenticated_returns_401(self):
        """No JWT returns 401."""
        self.client.credentials()
        response = self.client.patch(
            self._url(), {"mood": "happy"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mood_patch_now_includes_reflection_prompt(self):
        """Mood save creates reflection_prompt message after mood_response."""
        response = self.client.patch(
            self._url(), {"mood": "happy"}, format="json"
        )
        messages = response.data["messages"]
        prompt_msgs = [m for m in messages if m["message_type"] == "reflection_prompt"]
        self.assertEqual(len(prompt_msgs), 1)
        self.assertEqual(prompt_msgs[0]["sender"], "bot")
        self.assertEqual(prompt_msgs[0]["order"], 3)  # greeting=0, mood_prompt=1, mood_response=2, reflection_prompt=3

    def test_patch_mood_and_response_together_returns_400(self):
        """Cannot send both mood and user_response in the same request."""
        response = self.client.patch(
            self._url(), {"mood": "happy", "user_response": "I feel great"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReflectionAPITest(APITestCase):
    """Tests for the PATCH /api/chats/<pk>/ endpoint — reflection submission."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="reflect@example.com",
            password=None,
            display_name="Reflect User",
            auth_provider="google",
            auth_provider_id="google-reflect-1",
            timezone="America/New_York",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
        self.chat = DailyChat.objects.create(
            user=self.user, date=date(2026, 3, 3), mood="happy"
        )
        ChatMessage.objects.bulk_create([
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.BOT,
                message_type=ChatMessage.MessageType.GREETING,
                content="Good morning!",
                order=0,
            ),
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.BOT,
                message_type=ChatMessage.MessageType.MOOD_PROMPT,
                content="How are you feeling?",
                order=1,
            ),
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.USER,
                message_type=ChatMessage.MessageType.MOOD_RESPONSE,
                content="Happy 😊",
                order=2,
            ),
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.BOT,
                message_type=ChatMessage.MessageType.REFLECTION_PROMPT,
                content="Take a moment to share what's on your mind.",
                order=3,
            ),
        ])

    def _url(self, pk=None):
        return f"/api/chats/{pk or self.chat.pk}/"

    @patch("api.services.llm_service.generate_acknowledgment")
    def test_patch_reflection_success(self, mock_llm):
        """AC3: Reflection saved, acknowledgment returned."""
        mock_llm.return_value = "It sounds like today brought you real joy. The way you're celebrating these good moments shows a beautiful presence and awareness. Hold onto this feeling—it's truly worth honoring."
        response = self.client.patch(
            self._url(), {"user_response": "Today was a great day!"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

    @patch("api.services.llm_service.generate_acknowledgment")
    def test_patch_reflection_creates_messages(self, mock_llm):
        """AC3: reflection_response + acknowledgment messages created."""
        mock_llm.return_value = "Gratitude is such a grounding place to be. The fact that you're taking time to notice and honor what brings you joy speaks volumes about your heart. Keep cultivating this beautiful awareness."
        response = self.client.patch(
            self._url(), {"user_response": "Feeling grateful"}, format="json"
        )
        messages = response.data["messages"]
        reflection_msgs = [m for m in messages if m["message_type"] == "reflection_response"]
        ack_msgs = [m for m in messages if m["message_type"] == "acknowledgment"]
        self.assertEqual(len(reflection_msgs), 1)
        self.assertEqual(reflection_msgs[0]["sender"], "user")
        self.assertEqual(reflection_msgs[0]["content"], "Feeling grateful")
        self.assertEqual(len(ack_msgs), 1)
        self.assertEqual(ack_msgs[0]["sender"], "bot")

    @patch("api.services.llm_service.generate_acknowledgment")
    def test_patch_reflection_llm_called_with_correct_args(self, mock_llm):
        """LLM service is called with the correct mood and reflection text."""
        mock_llm.return_value = "It sounds like you're in a genuinely good place right now, and that's beautiful. Life feels manageable when we slow down to notice it, and you're doing exactly that. Hold onto this feeling—it matters."
        self.client.patch(
            self._url(), {"user_response": "Life is good"}, format="json"
        )
        mock_llm.assert_called_once_with("happy", "Life is good")

    @patch("api.services.llm_service.generate_acknowledgment")
    def test_patch_reflection_acknowledgment_uses_llm_response(self, mock_llm):
        """AC5: Acknowledgment content comes from the LLM service."""
        mock_llm.return_value = "What a gift that life feels good to you right now. The ease and contentment you're expressing is beautiful, and you're really honoring that. Keep nurturing this sense of wellbeing."

        response = self.client.patch(
            self._url(), {"user_response": "Life is good"}, format="json"
        )
        ack = [m for m in response.data["messages"] if m["message_type"] == "acknowledgment"][0]
        self.assertEqual(ack["content"], "What a gift that life feels good to you right now. The ease and contentment you're expressing is beautiful, and you're really honoring that. Keep nurturing this sense of wellbeing.")

        # Test with a down mood
        chat2 = DailyChat.objects.create(
            user=self.user, date=date(2026, 3, 4), mood="down"
        )
        ChatMessage.objects.create(
            daily_chat=chat2,
            sender=ChatMessage.SenderChoice.BOT,
            message_type=ChatMessage.MessageType.REFLECTION_PROMPT,
            content="Share your thoughts...",
            order=0,
        )
        mock_llm.return_value = "I hear that today has been really difficult, and I'm glad you're here sharing about it. It takes courage to face tough days, and acknowledging what's hard is the first step through it. Be gentle with yourself—better days are ahead."
        response2 = self.client.patch(
            self._url(chat2.pk), {"user_response": "Tough day"}, format="json"
        )
        ack2 = [m for m in response2.data["messages"] if m["message_type"] == "acknowledgment"][0]
        self.assertEqual(ack2["content"], "I hear that today has been really difficult, and I'm glad you're here sharing about it. It takes courage to face tough days, and acknowledging what's hard is the first step through it. Be gentle with yourself—better days are ahead.")
        mock_llm.assert_called_with("down", "Tough day")

    @patch("api.services.llm_service.generate_acknowledgment")
    def test_patch_reflection_llm_fallback(self, mock_llm):
        """When LLM fails, the fallback message is used and chat still completes."""
        from api.services.llm_service import FALLBACK_MESSAGE

        mock_llm.return_value = FALLBACK_MESSAGE

        response = self.client.patch(
            self._url(), {"user_response": "Testing fallback"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")
        ack = [m for m in response.data["messages"] if m["message_type"] == "acknowledgment"][0]
        self.assertEqual(ack["content"], FALLBACK_MESSAGE)

    @patch("api.services.llm_service.generate_acknowledgment")
    def test_patch_reflection_marks_completed(self, mock_llm):
        """AC6: Status = completed, completed_at set."""
        mock_llm.return_value = "Well done!"
        response = self.client.patch(
            self._url(), {"user_response": "All done"}, format="json"
        )
        self.assertEqual(response.data["status"], "completed")
        self.assertIsNotNone(response.data["completed_at"])

    def test_patch_reflection_empty_string_returns_400(self):
        """AC2: Empty reflection rejected."""
        response = self.client.patch(
            self._url(), {"user_response": ""}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_reflection_whitespace_only_returns_400(self):
        """AC2: Whitespace-only rejected."""
        response = self.client.patch(
            self._url(), {"user_response": "   "}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_reflection_without_mood_returns_400(self):
        """Cannot submit reflection before mood is set."""
        no_mood_chat = DailyChat.objects.create(
            user=self.user, date=date(2026, 3, 5)
        )
        response = self.client.patch(
            self._url(no_mood_chat.pk), {"user_response": "Hello"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("api.services.llm_service.generate_acknowledgment")
    def test_patch_reflection_already_completed_returns_400(self, mock_llm):
        """Cannot submit reflection twice."""
        mock_llm.return_value = "Thank you for sharing!"
        self.client.patch(
            self._url(), {"user_response": "First reflection"}, format="json"
        )
        response = self.client.patch(
            self._url(), {"user_response": "Second reflection"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CompletedChatAPITest(APITestCase):
    """Tests for Story 007: completed chats are read-only."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="completed@example.com",
            password=None,
            display_name="Completed User",
            auth_provider="google",
            auth_provider_id="google-completed-1",
            timezone="America/New_York",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
        self.chat = DailyChat.objects.create(
            user=self.user, date=date(2026, 3, 30), mood="happy", status="completed"
        )
        ChatMessage.objects.bulk_create([
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.BOT,
                message_type=ChatMessage.MessageType.GREETING,
                content="Good morning!",
                order=0,
            ),
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.BOT,
                message_type=ChatMessage.MessageType.MOOD_PROMPT,
                content="How are you feeling?",
                order=1,
            ),
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.USER,
                message_type=ChatMessage.MessageType.MOOD_RESPONSE,
                content="Happy 😊",
                order=2,
            ),
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.BOT,
                message_type=ChatMessage.MessageType.REFLECTION_PROMPT,
                content="Share your thoughts...",
                order=3,
            ),
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.USER,
                message_type=ChatMessage.MessageType.REFLECTION_RESPONSE,
                content="Today was great!",
                order=4,
            ),
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.BOT,
                message_type=ChatMessage.MessageType.ACKNOWLEDGMENT,
                content="Thank you for sharing!",
                order=5,
            ),
        ])

    def _url(self, pk=None):
        return f"/api/chats/{pk or self.chat.pk}/"

    def test_patch_completed_chat_with_mood_returns_400(self):
        """AC5: PATCH mood on a completed chat is rejected."""
        response = self.client.patch(
            self._url(), {"mood": "calm"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("completed", response.data["detail"])

    def test_patch_completed_chat_with_reflection_returns_400(self):
        """AC5: PATCH user_response on a completed chat is rejected."""
        response = self.client.patch(
            self._url(), {"user_response": "New reflection"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("completed", response.data["detail"])

    def test_get_today_returns_completed_chat(self):
        """AC5: GET /api/chats/today/ returns existing completed chat (no duplicate)."""
        response = self.client.get("/api/chats/today/?date=2026-03-30")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.chat.pk)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(DailyChat.objects.filter(user=self.user, date=date(2026, 3, 30)).count(), 1)

    def test_get_today_next_day_creates_new_chat(self):
        """AC4: GET /api/chats/today/ on a new date creates a fresh chat."""
        response = self.client.get("/api/chats/today/?date=2026-03-31")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "in_progress")
        self.assertNotEqual(response.data["id"], self.chat.pk)
        self.assertEqual(DailyChat.objects.filter(user=self.user).count(), 2)


class LLMServiceTest(TestCase):
    """Unit tests for the LLM service module."""

    @patch("api.services.llm_service._client")
    def test_generate_acknowledgment_success(self, mock_client):
        """Successful API call returns the model's response."""
        from api.services.llm_service import generate_acknowledgment

        mock_choice = type("Choice", (), {
            "message": type("Message", (), {
                "content": " What a gift to hear that today was wonderful! The joy you're expressing is truly beautiful, and it sounds like you were really present to those good moments. Keep celebrating these wins—they're worth savoring. "
            })()
        })()
        mock_response = type("Response", (), {"choices": [mock_choice]})()
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_acknowledgment("happy", "I had a wonderful day")

        self.assertEqual(result, "What a gift to hear that today was wonderful! The joy you're expressing is truly beautiful, and it sounds like you were really present to those good moments. Keep celebrating these wins—they're worth savoring.")
        mock_client.chat.completions.create.assert_called_once()

    @patch("api.services.llm_service._client")
    def test_generate_acknowledgment_fallback_on_error(self, mock_client):
        """API error returns the fallback message."""
        from api.services.llm_service import FALLBACK_MESSAGE, generate_acknowledgment
        from openai import OpenAIError

        mock_client.chat.completions.create.side_effect = OpenAIError("API down")

        result = generate_acknowledgment("down", "Bad day")

        self.assertEqual(result, FALLBACK_MESSAGE)

    @patch("api.services.llm_service._client")
    def test_generate_acknowledgment_system_prompt_includes_mood(self, mock_client):
        """System prompt sent to OpenAI includes the user's mood."""
        from api.services.llm_service import generate_acknowledgment

        mock_choice = type("Choice", (), {
            "message": type("Message", (), {
                "content": "It sounds like today has been really frustrating, and that's completely valid. When everything feels overwhelming, it can be hard to see the path forward, but you're here reflecting on it, which shows real strength. Trust that this will pass."
            })()
        })()
        mock_response = type("Response", (), {"choices": [mock_choice]})()
        mock_client.chat.completions.create.return_value = mock_response

        generate_acknowledgment("frustrated", "Everything went wrong")

        call_kwargs = mock_client.chat.completions.create.call_args
        system_message = call_kwargs.kwargs["messages"][0]
        self.assertEqual(system_message["role"], "system")
        self.assertIn("frustrated", system_message["content"])

    @patch("api.services.llm_service._client")
    def test_generate_acknowledgment_sends_reflection_as_user_message(self, mock_client):
        """The reflection text is sent as the user message to OpenAI."""
        from api.services.llm_service import generate_acknowledgment

        mock_choice = type("Choice", (), {
            "message": type("Message", (), {
                "content": "What a lovely place to be in your day. There's real value in the peace you're experiencing, and taking time to notice and protect that calm is beautiful. Continue honoring this serenity—it's a gift you're giving yourself."
            })()
        })()
        mock_response = type("Response", (), {"choices": [mock_choice]})()
        mock_client.chat.completions.create.return_value = mock_response

        generate_acknowledgment("calm", "Feeling peaceful today")

        call_kwargs = mock_client.chat.completions.create.call_args
        user_message = call_kwargs.kwargs["messages"][1]
        self.assertEqual(user_message["role"], "user")
        self.assertEqual(user_message["content"], "Feeling peaceful today")


class DailyChatDetailGetAPITest(APITestCase):
    """Tests for GET /api/chats/<pk>/ endpoint."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="detail@example.com",
            password=None,
            display_name="Detail User",
            auth_provider="google",
            auth_provider_id="google-detail-1",
            timezone="America/New_York",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
        self.chat = DailyChat.objects.create(
            user=self.user, date=date(2026, 3, 10), mood="happy", status="completed"
        )
        ChatMessage.objects.bulk_create([
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.BOT,
                message_type=ChatMessage.MessageType.GREETING,
                content="Good morning!",
                order=0,
            ),
            ChatMessage(
                daily_chat=self.chat,
                sender=ChatMessage.SenderChoice.USER,
                message_type=ChatMessage.MessageType.REFLECTION_RESPONSE,
                content="Today was great!",
                order=4,
            ),
        ])

    def _url(self, pk=None):
        return f"/api/chats/{pk or self.chat.pk}/"

    def test_get_returns_full_chat(self):
        """GET returns 200 with full chat data including messages."""
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.chat.pk)
        self.assertEqual(response.data["mood"], "happy")
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(len(response.data["messages"]), 2)
        self.assertIn("started_at", response.data)
        self.assertIn("completed_at", response.data)

    def test_get_nonexistent_returns_404(self):
        """GET with invalid ID returns 404."""
        response = self.client.get(self._url(pk=99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_other_users_chat_returns_404(self):
        """User cannot GET another user's chat."""
        other_user = User.objects.create_user(
            email="other-detail@example.com",
            password=None,
            display_name="Other Detail",
            auth_provider="google",
            auth_provider_id="google-other-detail-1",
        )
        other_chat = DailyChat.objects.create(
            user=other_user, date=date(2026, 3, 11), mood="calm", status="completed"
        )
        response = self.client.get(self._url(pk=other_chat.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_unauthenticated_returns_401(self):
        """No JWT returns 401."""
        self.client.credentials()
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MonthlyChatAPITest(APITestCase):
    """Tests for the GET /api/chats/monthly/ endpoint."""

    MONTHLY_URL = "/api/chats/monthly/"

    def setUp(self):
        self.user = User.objects.create_user(
            email="monthly@example.com",
            password=None,
            display_name="Monthly User",
            auth_provider="google",
            auth_provider_id="google-monthly-1",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

    def _create_chat(self, user, chat_date, mood="happy", chat_status="completed"):
        return DailyChat.objects.create(
            user=user,
            date=chat_date,
            mood=mood,
            status=chat_status,
        )

    def test_returns_completed_chats_only(self):
        """Only completed chats are returned; in-progress chats are excluded."""
        self._create_chat(self.user, date(2026, 3, 1), mood="happy", chat_status="completed")
        self._create_chat(self.user, date(2026, 3, 2), mood="calm", chat_status="in_progress")

        response = self.client.get(f"{self.MONTHLY_URL}?year=2026&month=3")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["date"], "2026-03-01")
        self.assertEqual(response.data[0]["mood"], "happy")

    def test_returns_correct_fields(self):
        """Response contains only id, date, and mood (no messages)."""
        self._create_chat(self.user, date(2026, 3, 15), mood="neutral")

        response = self.client.get(f"{self.MONTHLY_URL}?year=2026&month=3")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entry = response.data[0]
        self.assertIn("id", entry)
        self.assertIn("date", entry)
        self.assertIn("mood", entry)
        self.assertNotIn("messages", entry)
        self.assertNotIn("started_at", entry)

    def test_returns_empty_list_for_month_with_no_chats(self):
        """An empty list is returned for a month with no completed chats."""
        response = self.client.get(f"{self.MONTHLY_URL}?year=2026&month=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_returns_400_if_year_missing(self):
        """Missing year parameter returns 400."""
        response = self.client.get(f"{self.MONTHLY_URL}?month=3")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_if_month_missing(self):
        """Missing month parameter returns 400."""
        response = self.client.get(f"{self.MONTHLY_URL}?year=2026")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_for_invalid_month(self):
        """Invalid month values (0, 13, non-numeric) return 400."""
        for month_val in ["0", "13", "abc"]:
            response = self.client.get(f"{self.MONTHLY_URL}?year=2026&month={month_val}")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_isolation(self):
        """A user only sees their own chats, not another user's."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password=None,
            display_name="Other User",
            auth_provider="google",
            auth_provider_id="google-other-1",
        )
        self._create_chat(self.user, date(2026, 3, 5), mood="happy")
        self._create_chat(other_user, date(2026, 3, 5), mood="down")

        response = self.client.get(f"{self.MONTHLY_URL}?year=2026&month=3")

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["mood"], "happy")

    def test_requires_authentication(self):
        """Unauthenticated requests return 401."""
        self.client.credentials()  # Remove auth
        response = self.client.get(f"{self.MONTHLY_URL}?year=2026&month=3")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ordered_by_date(self):
        """Results are ordered by date ascending."""
        self._create_chat(self.user, date(2026, 3, 20), mood="calm")
        self._create_chat(self.user, date(2026, 3, 5), mood="happy")
        self._create_chat(self.user, date(2026, 3, 12), mood="neutral")

        response = self.client.get(f"{self.MONTHLY_URL}?year=2026&month=3")

        dates = [entry["date"] for entry in response.data]
        self.assertEqual(dates, ["2026-03-05", "2026-03-12", "2026-03-20"])


class ProfileStatsAPITest(APITestCase):
    """Tests for GET /api/profile/stats/"""

    STATS_URL = "/api/profile/stats/"

    def setUp(self):
        self.user = User.objects.create_user(
            email="stats@example.com",
            display_name="Stats User",
            auth_provider="google",
            auth_provider_id="stats-123",
            timezone="UTC",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def _create_completed_chat(self, user, chat_date, mood="happy"):
        chat = DailyChat.objects.create(
            user=user,
            date=chat_date,
            mood=mood,
            status=DailyChat.StatusChoice.COMPLETED,
        )
        return chat

    def _create_in_progress_chat(self, user, chat_date):
        return DailyChat.objects.create(
            user=user,
            date=chat_date,
            status=DailyChat.StatusChoice.IN_PROGRESS,
        )

    def test_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(self.STATS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_zero_state_no_chats(self):
        """AC5: New user with no chats gets all zeros and null mood."""
        response = self.client.get(self.STATS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_chats"], 0)
        self.assertEqual(response.data["current_streak"], 0)
        self.assertEqual(response.data["longest_streak"], 0)
        self.assertIsNone(response.data["most_frequent_mood"])

    def test_total_chats_counts_completed_only(self):
        """In-progress chats are excluded from total."""
        today = date.today()
        self._create_completed_chat(self.user, today - timedelta(days=2))
        self._create_completed_chat(self.user, today - timedelta(days=1))
        self._create_in_progress_chat(self.user, today)

        response = self.client.get(self.STATS_URL)
        self.assertEqual(response.data["total_chats"], 2)

    @patch("django.utils.timezone.now")
    def test_current_streak_including_today(self, mock_now):
        """Current streak counts consecutive days ending today."""
        mock_now.return_value = datetime(2026, 3, 5, 12, 0, tzinfo=ZoneInfo("UTC"))
        self._create_completed_chat(self.user, date(2026, 3, 3))
        self._create_completed_chat(self.user, date(2026, 3, 4))
        self._create_completed_chat(self.user, date(2026, 3, 5))

        response = self.client.get(self.STATS_URL)
        self.assertEqual(response.data["current_streak"], 3)

    @patch("django.utils.timezone.now")
    def test_current_streak_ending_yesterday(self, mock_now):
        """Current streak includes yesterday if no chat today."""
        mock_now.return_value = datetime(2026, 3, 5, 12, 0, tzinfo=ZoneInfo("UTC"))
        self._create_completed_chat(self.user, date(2026, 3, 3))
        self._create_completed_chat(self.user, date(2026, 3, 4))
        # No chat on 2026-03-05

        response = self.client.get(self.STATS_URL)
        self.assertEqual(response.data["current_streak"], 2)

    @patch("django.utils.timezone.now")
    def test_current_streak_broken_by_gap(self, mock_now):
        """Current streak resets when there's a gap."""
        mock_now.return_value = datetime(2026, 3, 5, 12, 0, tzinfo=ZoneInfo("UTC"))
        self._create_completed_chat(self.user, date(2026, 3, 1))
        self._create_completed_chat(self.user, date(2026, 3, 2))
        # gap on 2026-03-03
        self._create_completed_chat(self.user, date(2026, 3, 4))
        self._create_completed_chat(self.user, date(2026, 3, 5))

        response = self.client.get(self.STATS_URL)
        self.assertEqual(response.data["current_streak"], 2)

    @patch("django.utils.timezone.now")
    def test_current_streak_zero_when_last_chat_before_yesterday(self, mock_now):
        """Current streak is 0 if last chat was more than 1 day ago."""
        mock_now.return_value = datetime(2026, 3, 5, 12, 0, tzinfo=ZoneInfo("UTC"))
        self._create_completed_chat(self.user, date(2026, 3, 1))
        self._create_completed_chat(self.user, date(2026, 3, 2))

        response = self.client.get(self.STATS_URL)
        self.assertEqual(response.data["current_streak"], 0)

    def test_longest_streak_across_history(self):
        """Longest streak finds the longest consecutive run ever."""
        today = date.today()
        # First run: 3 days
        self._create_completed_chat(self.user, today - timedelta(days=20))
        self._create_completed_chat(self.user, today - timedelta(days=19))
        self._create_completed_chat(self.user, today - timedelta(days=18))
        # Gap
        # Second run: 5 days
        self._create_completed_chat(self.user, today - timedelta(days=10))
        self._create_completed_chat(self.user, today - timedelta(days=9))
        self._create_completed_chat(self.user, today - timedelta(days=8))
        self._create_completed_chat(self.user, today - timedelta(days=7))
        self._create_completed_chat(self.user, today - timedelta(days=6))
        # Gap
        # Third run: 2 days
        self._create_completed_chat(self.user, today - timedelta(days=2))
        self._create_completed_chat(self.user, today - timedelta(days=1))

        response = self.client.get(self.STATS_URL)
        self.assertEqual(response.data["longest_streak"], 5)

    def test_most_frequent_mood(self):
        """Most frequent mood returns the mode across completed chats."""
        today = date.today()
        self._create_completed_chat(self.user, today - timedelta(days=5), mood="happy")
        self._create_completed_chat(self.user, today - timedelta(days=4), mood="calm")
        self._create_completed_chat(self.user, today - timedelta(days=3), mood="calm")
        self._create_completed_chat(self.user, today - timedelta(days=2), mood="calm")
        self._create_completed_chat(self.user, today - timedelta(days=1), mood="happy")

        response = self.client.get(self.STATS_URL)
        mood = response.data["most_frequent_mood"]
        self.assertEqual(mood["value"], "calm")
        self.assertEqual(mood["label"], "Calm")
        self.assertIn(mood["emoji"], "😌")

    def test_in_progress_chats_excluded(self):
        """In-progress chats are excluded from all stats."""
        today = date.today()
        self._create_in_progress_chat(self.user, today - timedelta(days=1))
        self._create_in_progress_chat(self.user, today)

        response = self.client.get(self.STATS_URL)
        self.assertEqual(response.data["total_chats"], 0)
        self.assertEqual(response.data["current_streak"], 0)
        self.assertEqual(response.data["longest_streak"], 0)
        self.assertIsNone(response.data["most_frequent_mood"])

    def test_other_users_data_excluded(self):
        """Stats only count the authenticated user's chats."""
        other_user = User.objects.create_user(
            email="other@example.com",
            display_name="Other",
            auth_provider="google",
            auth_provider_id="other-456",
        )
        today = date.today()
        self._create_completed_chat(other_user, today - timedelta(days=1))
        self._create_completed_chat(self.user, today - timedelta(days=2))

        response = self.client.get(self.STATS_URL)
        self.assertEqual(response.data["total_chats"], 1)

    def test_single_chat_longest_streak_is_one(self):
        """A single completed chat gives longest streak of 1."""
        self._create_completed_chat(self.user, date.today() - timedelta(days=5))

        response = self.client.get(self.STATS_URL)
        self.assertEqual(response.data["longest_streak"], 1)


class ProfileViewDateJoinedTest(APITestCase):
    """Verify that GET /api/me/ now includes date_joined."""

    def test_date_joined_in_response(self):
        user = User.objects.create_user(
            email="joined@example.com",
            display_name="Joined User",
            auth_provider="google",
            auth_provider_id="joined-123",
        )
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        response = self.client.get("/api/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("date_joined", response.data)
