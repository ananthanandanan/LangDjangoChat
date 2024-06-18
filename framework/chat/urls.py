from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

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
    ## NOTE: API endpoint to get the auth token
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("chatroom/", views.chat, name="chatroom"),
    path("log-in/", views.login_view, name="log-in"),
]
