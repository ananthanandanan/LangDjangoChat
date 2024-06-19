import solara
import solara.lab
import json
import asyncio
import websockets
from typing import List, Dict
from typing_extensions import TypedDict
import requests


class MessageDict(TypedDict):
    role: str
    content: str
    stream_id: str


token: solara.Reactive[str] = solara.reactive("")
thread_id: solara.Reactive[str] = solara.reactive("")
websocket: solara.Reactive[websockets.WebSocketClientProtocol] = solara.reactive(None)
auth_token: solara.Reactive[str] = solara.reactive("")
is_connected: solara.Reactive[bool] = solara.reactive(False)
messages: solara.Reactive[List[MessageDict]] = solara.reactive([])


@solara.component
def ChatPage():
    user_message_count = solara.reactive(0)

    def update_message_content(
        messages: List[MessageDict], target_stream_id: str, new_content: str
    ) -> List[MessageDict]:
        updated_messages = []
        for message in messages:
            if message["stream_id"] == target_stream_id:
                updated_message = {
                    "role": message["role"],
                    "content": message["content"] + new_content,
                    "stream_id": message["stream_id"],
                }
                updated_messages.append(updated_message)
            else:
                updated_messages.append(message)
        return updated_messages

    async def connect_websocket():
        if is_connected.value:
            return  # Prevent creating multiple WebSocket connections

        websocket_url = (
            f"ws://localhost:8000/ws/chat/{thread_id.value}/?token={token.value}"
        )
        try:
            ws = await websockets.connect(websocket_url)
            websocket.value = ws
            is_connected.value = True

            try:
                async for message in ws:
                    data = json.loads(message)
                    handle_websocket_message(data)
            finally:
                await ws.close()
                websocket.value = None
                is_connected.value = False
        except asyncio.CancelledError:
            print("WebSocket connection task was cancelled.")
        except Exception as e:
            print(f"WebSocket connection error: {e}")

    def handle_websocket_message(data):
        if data["category"] == "chat_log":
            if data["sender"] == "Bot":
                messages.value = [
                    *messages.value,
                    {"role": "assistant", "content": data["message"], "stream_id": ""},
                ]
            else:
                messages.value = [
                    *messages.value,
                    {"role": "user", "content": data["message"], "stream_id": ""},
                ]
        elif data["category"] == "user_message":
            messages.value = [
                *messages.value,
                {"role": "user", "content": data["message"], "stream_id": ""},
            ]
        elif data["category"] in ["stream_start", "stream_chunk", "stream_end"]:
            stream_id = data["stream_id"]
            if data["category"] == "stream_start":
                messages.value = [
                    *messages.value,
                    {"role": "assistant", "content": "", "stream_id": stream_id},
                ]
            elif data["category"] == "stream_chunk":
                updated_messages = update_message_content(
                    messages.value, stream_id, data["message"]
                )
                messages.value = updated_messages
            elif data["category"] == "stream_end":
                pass

    async def send_message(message):
        if websocket.value:
            await websocket.value.send(json.dumps({"message": message}))

    def send(message):
        user_message_count.value += 1  # Update reactively
        asyncio.create_task(
            send_message(message)
        )  # Send message immediately after updating

    def start_connection():
        asyncio.create_task(connect_websocket())

    def stop_connection():
        if websocket.value:
            asyncio.create_task(websocket.value.close())
        is_connected.value = False

    solara.use_effect(start_connection, [])
    solara.use_effect(stop_connection, [])
    ## Center the chat box style
    with solara.Column(
        style={
            "width": "100vw",
            "height": "100vh",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "padding": "20px",
        }
    ):
        ## Show the Thread ID
        solara.Markdown(f"## Thread ID: {thread_id.value}")
        with solara.lab.ChatBox():
            for item in messages.value:
                with solara.lab.ChatMessage(
                    user=item["role"] == "user",
                    avatar=False,
                    name="ChatGPT" if item["role"] == "assistant" else "User",
                    color=(
                        "rgba(0,0,0, 0.06)"
                        if item["role"] == "assistant"
                        else "#ff991f"
                    ),
                    avatar_background_color=(
                        "primary" if item["role"] == "assistant" else None
                    ),
                    border_radius="20px",
                ):
                    solara.Markdown(item["content"])
        solara.lab.ChatInput(send_callback=send, style={"width": "50%"})


@solara.component
def LoginPage():
    email: solara.Reactive[str] = solara.reactive("")
    password: solara.Reactive[str] = solara.reactive("")
    login_error = solara.reactive("")

    async def get_auth_token():
        response = requests.post(
            "http://localhost:8000/chat/api-token-auth/",
            json={"username": email.value, "password": password.value},
        )
        if response.status_code == 200:
            auth_token.value = response.json()["token"]
        return response

    async def login():
        auth_response = await get_auth_token()

        if auth_response.status_code != 200:
            login_error.value = "Invalid credentials"
            return
        else:
            response = requests.post(
                "http://localhost:8000/chat/log-in/",
                json={"email": email.value, "password": password.value},
                headers={"Authorization": f"Token {auth_token.value}"},
            )
            if response.status_code == 200:
                token.value = response.json()["token"]
                ThreadPage()
            else:
                login_error.value = "Invalid credentials"

    with solara.Column(
        style={
            "width": "800px",
            "height": "400px",
            "display": "flex",
            "flexDirection": "column",
            "AlignItems": "center",
            "justifyContent": "center",
            "margin": "auto",
        }
    ):
        solara.Markdown("# Login")
        solara.InputText(label="Email", value=email)
        solara.InputText(label="Password", value=password, password=True)
        solara.Button("Login", on_click=solara.lab.use_task(login))
        if login_error.value:
            solara.Text(login_error.value, style={"color": "red"})


@solara.component
def ThreadPage():
    input_thread_id: solara.Reactive[str] = solara.reactive("")

    def join_thread():
        thread_id.value = input_thread_id.value
        ChatPage()

    def create_thread():
        thread_id.value = input_thread_id.value or generate_uuid()
        ChatPage()

    with solara.Column(
        style={
            "width": "400px",
            "margin": "0 auto",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "justifyContent": "center",
        }
    ):
        solara.Markdown("# Join or Create Thread")
        solara.InputText(label="Thread ID", value=input_thread_id)
        solara.Button("Join Thread", on_click=join_thread)
        solara.Button("Create Thread", on_click=create_thread)


def generate_uuid():
    import uuid

    return str(uuid.uuid4())


@solara.component
def Page():
    solara.Style(
        """
    html, body, #root {
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0;
    }
    """
    )
    if not token.value:
        LoginPage()
    elif not thread_id.value:
        ThreadPage()
    else:
        ChatPage()
