from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager for User model where email is the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model for OAuth-based authentication."""

    email = models.EmailField("email address", unique=True)
    username = models.CharField(max_length=150, blank=True, default="")

    objects = UserManager()

    AUTH_PROVIDER_CHOICES = [
        ("google", "Google"),
        ("apple", "Apple"),
    ]
    auth_provider = models.CharField(max_length=10, choices=AUTH_PROVIDER_CHOICES)
    auth_provider_id = models.CharField(
        max_length=255,
        help_text="Provider-specific user ID (Google sub, Apple sub)",
    )
    display_name = models.CharField(max_length=100)
    avatar_emoji = models.CharField(max_length=10, default="\U0001f60a")
    timezone = models.CharField(
        max_length=63, default="UTC", help_text="IANA timezone string"
    )
    reminder_enabled = models.BooleanField(default=True)
    reminder_time = models.TimeField(
        default="20:00", help_text="Local time for daily reminder"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["display_name"]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["auth_provider", "auth_provider_id"],
                name="unique_provider_account",
            ),
        ]

    def __str__(self):
        return self.display_name


class Item(models.Model):
    """Example starter model."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DailyChat(models.Model):
    """One chat session per user per day for guided journaling."""

    class StatusChoice(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    class MoodChoice(models.TextChoices):
        HAPPY = "happy", "Happy"
        CALM = "calm", "Calm"
        NEUTRAL = "neutral", "Neutral"
        DOWN = "down", "Down"
        FRUSTRATED = "frustrated", "Frustrated"

    MOOD_DISPLAY = {
        "happy": "Happy 😊",
        "calm": "Calm 😌",
        "neutral": "Neutral 😐",
        "down": "Down 😔",
        "frustrated": "Frustrated 😤",
    }

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="daily_chats"
    )
    date = models.DateField()
    mood = models.CharField(
        max_length=50, blank=True, default="", choices=MoodChoice.choices
    )
    summary = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=StatusChoice.choices,
        default=StatusChoice.IN_PROGRESS,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "date"],
                name="one_chat_per_user_per_day",
            ),
        ]

    def __str__(self):
        return f"{self.user.display_name} — {self.date}"


class ChatMessage(models.Model):
    """Individual message within a daily chat session."""

    class SenderChoice(models.TextChoices):
        BOT = "bot", "Bot"
        USER = "user", "User"

    class MessageType(models.TextChoices):
        GREETING = "greeting", "Greeting"
        MOOD_PROMPT = "mood_prompt", "Mood Prompt"
        MOOD_RESPONSE = "mood_response", "Mood Response"
        REFLECTION_PROMPT = "reflection_prompt", "Reflection Prompt"
        REFLECTION_RESPONSE = "reflection_response", "Reflection Response"
        ACKNOWLEDGMENT = "acknowledgment", "Acknowledgment"

    daily_chat = models.ForeignKey(
        DailyChat, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(
        max_length=10, choices=SenderChoice.choices
    )
    message_type = models.CharField(
        max_length=30, choices=MessageType.choices
    )
    content = models.TextField()
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["daily_chat", "order"],
                name="unique_message_order_per_chat",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_sender_display()} ({self.message_type}) "
            f"— {self.content[:50]}"
        )
