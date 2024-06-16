from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate

# Create your views here.
from .models import ChatThread, ChatMessage
from .serializers import ChatThreadSerializer, ChatMessageSerializer
from rest_framework.permissions import IsAuthenticated

from rest_framework import viewsets
from django.views import View
from members.forms import MembersCreationForm
from rest_framework.authtoken.models import Token


class ChatThreadViewSet(viewsets.ModelViewSet):
    serializer_class = ChatThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatThread.objects.filter(author=self.request.user)


class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(thread=self.kwargs["thread_id"])


## TODO: Convert the register and login views to use Django REST Framework API views for more production-ready code
class RegisterView(View):
    def get(self, request):
        form = MembersCreationForm()
        return render(request, "chat/register.html", {"form": form})

    def post(self, request):
        form = MembersCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            token, created = Token.objects.get_or_create(user=user)
            login(request, user)
            return redirect("chatroom")
        return render(request, "chat/register.html", {"form": form})


class LoginView(View):
    def get(self, request):
        return render(request, "chat/login.html")

    def post(self, request):
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return redirect("chatroom")
        return render(request, "chat/login.html", {"error": "Invalid credentials"})


def chat(request):
    token, created = Token.objects.get_or_create(user=request.user)
    return render(request, "chat/chat.html", {"token": token.key})
