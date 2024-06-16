from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter(trailing_slash=False)

(
    router.register(
        "threads/(?P<thread_id>[^/.]+)/messages",
        views.ChatMessageViewSet,
        basename="chatmessage",
    ),
)
(router.register("threads", views.ChatThreadViewSet, basename="chatthread"),)

urlpatterns = [
    path("", include(router.urls)),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
]
