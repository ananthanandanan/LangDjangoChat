import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatThread, ChatMessage
from members.models import Members
from .tasks import handle_chat_message

import logging

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope["url_route"]["kwargs"]["thread_id"]
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            logger.warning(f"Connection rejected for unauthenticated user.")
            return

        self.thread = await self.get_or_create_thread(self.thread_id, self.user)
        await self.channel_layer.group_add(self.thread_id, self.channel_name)
        await self.accept()
        await self.send_chat_logs()
        logger.info(f"User {self.user} connected to thread {self.thread_id}.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.thread_id, self.channel_name)
        logger.info(f"User {self.user} disconnected from thread {self.thread_id}.")

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        chat_message = await self.save_message(self.thread, self.user, message)
        await self.channel_layer.group_send(
            self.thread_id,
            {
                "type": "chat.message",
                "message": chat_message.content,
                "sender": chat_message.sender,
                "timestamp": chat_message.timestamp.isoformat(),
                "category": "user_message",
            },
        )
        handle_chat_message(self.thread_id, message)

    async def chat_message(self, event):
        category = event.get("category")
        timestamp = event.get("timestamp")
        stream_id = event.get("stream_id")
        chunk = event.get("chunk")
        response = event.get("response")
        message = event.get("message")
        sender = event.get("sender", "Bot")  # Default sender to "Bot"

        if category == "stream_start":
            await self.send(
                text_data=json.dumps(
                    {
                        "message": "",
                        "sender": sender,
                        "timestamp": timestamp,
                        "stream_id": stream_id,
                        "category": "stream_start",
                    }
                )
            )
        elif category == "stream_chunk":
            await self.send(
                text_data=json.dumps(
                    {
                        "message": chunk,
                        "sender": sender,
                        "timestamp": timestamp,
                        "stream_id": stream_id,
                        "category": "stream_chunk",
                    }
                )
            )
        elif category == "stream_end":
            _ = await self.save_message(self.thread, "B", response)
            await self.send(
                text_data=json.dumps(
                    {
                        "message": response,
                        "sender": sender,
                        "timestamp": timestamp,
                        "stream_id": stream_id,
                        "category": "stream_end",
                    }
                )
            )
        else:
            await self.send(
                text_data=json.dumps(
                    {
                        "message": message,
                        "sender": sender,
                        "timestamp": timestamp,
                        "category": category,
                    }
                )
            )

    async def send_chat_logs(self):
        messages = await self.get_chat_messages()
        for message in messages:
            await self.send(
                text_data=json.dumps(
                    {
                        "message": message.content,
                        "sender": message.sender_enum,
                        "timestamp": message.timestamp.isoformat(),
                        "category": "chat_log",
                    }
                )
            )

    @database_sync_to_async
    def get_or_create_thread(self, thread_id, user):
        user = Members.objects.get(email=user.email)
        thread, created = ChatThread.objects.get_or_create(
            id=thread_id,
            defaults={
                "name": f"Chat {thread_id}",
                "author": user,
                "organization": user.organization,
            },
        )
        return thread

    @database_sync_to_async
    def save_message(self, thread, user, content):
        if isinstance(user, Members):
            chat_message = ChatMessage.objects.create(
                thread=thread, content=content, sender="U"
            )
        else:
            chat_message = ChatMessage.objects.create(
                thread=thread, content=content, sender="B"
            )
        return chat_message

    @database_sync_to_async
    def get_chat_messages(self):
        return list(
            ChatMessage.objects.filter(thread=self.thread).order_by("timestamp")
        )
