from rest_framework import serializers

from rest_framework.exceptions import ValidationError

from .models import ChatMessage, DailyChat, Item, User


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class AppleAuthSerializer(serializers.Serializer):
    identity_token = serializers.CharField()
    user_name = serializers.CharField(required=False, allow_blank=True, default="")


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "display_name", "avatar_emoji", "timezone", "date_joined"]
        read_only_fields = ["id", "email", "date_joined"]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "sender", "message_type", "content", "order", "created_at"]
        read_only_fields = fields


class DailyChatSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = DailyChat
        fields = [
            "id",
            "date",
            "mood",
            "status",
            "started_at",
            "completed_at",
            "messages",
        ]
        read_only_fields = fields


class MoodDetailSerializer(serializers.Serializer):
    value = serializers.CharField()
    emoji = serializers.CharField()
    label = serializers.CharField()


class ProfileStatsSerializer(serializers.Serializer):
    total_chats = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    most_frequent_mood = MoodDetailSerializer(allow_null=True)


class MonthlyChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyChat
        fields = ["id", "date", "mood"]
        read_only_fields = fields


class DailyChatUpdateSerializer(serializers.Serializer):
    mood = serializers.ChoiceField(choices=DailyChat.MoodChoice.choices, required=False)
    user_response = serializers.CharField(required=False, max_length=5000)

    def validate_mood(self, value):
        if not value:
            raise ValidationError("Mood cannot be empty.")
        if self.instance and self.instance.mood:
            raise ValidationError("Mood has already been set.")
        return value

    def validate_user_response(self, value):
        if not value or not value.strip():
            raise ValidationError("Reflection cannot be empty.")
        if self.instance and self.instance.status == "completed":
            raise ValidationError("Chat is already completed.")
        if self.instance and not self.instance.mood:
            raise ValidationError("Mood must be set before submitting a reflection.")
        return value.strip()

    def validate(self, data):
        has_mood = "mood" in data and data["mood"]
        has_response = "user_response" in data and data["user_response"]
        if has_mood and has_response:
            raise ValidationError("Cannot send both mood and user_response in the same request.")
        if not has_mood and not has_response:
            raise ValidationError("Must provide either mood or user_response.")
        return data
