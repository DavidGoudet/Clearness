from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ChatMessage, DailyChat, Item, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for the custom User model."""

    list_display = ("email", "display_name", "auth_provider", "is_active", "date_joined")
    list_filter = ("auth_provider", "is_active", "is_staff")
    search_fields = ("email", "display_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Profile",
            {"fields": ("display_name", "avatar_emoji", "timezone")},
        ),
        (
            "Auth Provider",
            {"fields": ("auth_provider", "auth_provider_id")},
        ),
        (
            "Reminders",
            {"fields": ("reminder_enabled", "reminder_time")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "display_name",
                    "auth_provider",
                    "auth_provider_id",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


admin.site.register(Item)


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("sender", "message_type", "content", "order", "created_at")


@admin.register(DailyChat)
class DailyChatAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "mood", "status", "started_at")
    list_filter = ("status", "date")
    search_fields = ("user__email", "user__display_name")
    ordering = ("-date",)
    inlines = [ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("daily_chat", "sender", "message_type", "order", "created_at")
