from rest_framework import serializers
from .models import ChatMessage, ChatThread


class ChatThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatThread
        fields = ["id", "name", "author", "organization"]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "thread", "content", "sender", "timestamp"]
