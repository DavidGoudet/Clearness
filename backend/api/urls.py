from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AppleAuthView,
    DailyChatDetailView,
    GoogleAuthView,
    ItemViewSet,
    LogoutView,
    MonthlyChatListView,
    ProfileStatsView,
    ProfileView,
    TodayChatView,
)

router = DefaultRouter()
router.register(r"items", ItemViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/google/", GoogleAuthView.as_view(), name="auth-google"),
    path("auth/apple/", AppleAuthView.as_view(), name="auth-apple"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("profile/stats/", ProfileStatsView.as_view(), name="profile-stats"),
    path("chats/today/", TodayChatView.as_view(), name="chat-today"),
    path("chats/<int:pk>/", DailyChatDetailView.as_view(), name="chat-detail"),
    path("chats/monthly/", MonthlyChatListView.as_view(), name="chat-monthly"),
]
