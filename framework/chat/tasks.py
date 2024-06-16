from huey.contrib.djhuey import task
import logging
import uuid
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from chat.chatbot import app as chat_app
from django.utils import timezone
import logging


async def stream_response(thread_id, query):
    runnable = chat_app.chain
    stream_id = str(uuid.uuid4())
    channel_layer = get_channel_layer()

    def send(message):
        return channel_layer.group_send(thread_id, message)

    await send(
        {
            "type": "chat.message",
            "category": "stream_start",
            "stream_id": stream_id,
            "timestamp": timezone.now().isoformat(),  # Adding a unique timestamp
        }
    )

    response = ""
    async for chunk in runnable.astream({"input": query}):
        response += chunk.content
        logging.warning(f"Stream chunk: {chunk.content}")
        await send(
            {
                "type": "chat.message",
                "category": "stream_chunk",
                "stream_id": stream_id,
                "chunk": chunk.content,
                "timestamp": timezone.now().isoformat(),  # Adding a unique timestamp
            }
        )
    logging.warning(f"Stream response: {response}")
    await send(
        {
            "type": "chat.message",
            "category": "stream_end",
            "stream_id": stream_id,
            "response": response,
            "timestamp": timezone.now().isoformat(),  # Adding a unique timestamp
        }
    )


@task()
def handle_chat_message(thread_id, query):
    logging.warning(f"Handling chat message {thread_id} {query}")

    async_to_sync(stream_response)(thread_id, query)
