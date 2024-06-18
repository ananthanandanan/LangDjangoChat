import solara
import solara.lab
import json
import asyncio
import websockets
from typing import List
from typing_extensions import TypedDict
import requests


class MessageDict(TypedDict):
    role: str
    content: str


messages: solara.Reactive[List[MessageDict]] = solara.reactive([])
token: solara.Reactive[str] = solara.reactive("")
thread_id: solara.Reactive[str] = solara.reactive("")
websocket: solara.Reactive[websockets.WebSocketClientProtocol] = solara.reactive(None)
auth_token: solara.Reactive[str] = solara.reactive(
    "df1067116e92626ec05b3ff0bebdd39d9c719f1b"
)

# ## redirect
# def redirect(url):
#     router = solara.use_router()
#     router.push(url)


@solara.component
def ChatPage():
    user_message_count = len([m for m in messages.value if m["role"] == "user"])
    ongoing_messages = solara.reactive({})

    async def connect_websocket():
        websocket_url = (
            f"ws://localhost:8000/ws/chat/{thread_id.value}/?token={token.value}"
        )
        print("URL", websocket_url)
        ws = await websockets.connect(websocket_url)
        websocket.value = ws
        async for message in ws:
            data = json.loads(message)
            handle_websocket_message(data)

    def handle_websocket_message(data):
        if data["category"] == "user_message":
            messages.value.append({"role": "user", "content": data["message"]})
        elif data["category"] in ["stream_start", "stream_chunk", "stream_end"]:
            stream_id = data["stream_id"]
            if data["category"] == "stream_start":
                ongoing_messages.value[stream_id] = {"role": "assistant", "content": ""}
                messages.value.append(ongoing_messages.value[stream_id])
            elif data["category"] == "stream_chunk":
                ongoing_messages.value[stream_id]["content"] += data["message"]
                messages.value = messages.value  # Trigger reactive update
            elif data["category"] == "stream_end":
                del ongoing_messages.value[stream_id]

    async def send_message():
        if websocket.value:
            latest_message = messages.value[-1]
            await websocket.value.send(
                json.dumps({"message": latest_message["content"]})
            )

    solara.use_effect(solara.lab.use_task(connect_websocket), [])

    def send(message):
        messages.value.append({"role": "user", "content": message})

    solara.lab.use_task(send_message, dependencies=[user_message_count])

    with solara.Column(style={"width": "700px", "height": "50vh"}):
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
        solara.lab.ChatInput(send_callback=send)


@solara.component
def LoginPage():
    email: solara.Reactive[str] = solara.reactive("")
    password: solara.Reactive[str] = solara.reactive("")
    login_error = solara.reactive("")

    async def login():
        response = requests.post(
            "http://localhost:8000/chat/log-in/",
            json={"email": email.value, "password": password.value},
            headers={"Authorization": f"Token {auth_token.value}"},
        )
        if response.status_code == 200:
            print(response.json())
            token.value = response.json()["token"]
            print("Token", token.value)
            ThreadPage()
        else:
            login_error.value = "Invalid credentials"

    with solara.Column(style={"width": "400px", "margin": "0 auto"}):
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

    with solara.Column(style={"width": "400px", "margin": "0 auto"}):
        solara.Markdown("# Join or Create Thread")
        solara.InputText(label="Thread ID", value=input_thread_id)
        solara.Button("Join Thread", on_click=join_thread)
        solara.Button("Create Thread", on_click=create_thread)


def generate_uuid():
    import uuid

    return str(uuid.uuid4())


@solara.component
def Page():

    # routes = [
    #     solara.Route("/thread", component=ThreadPage, label="Thread"),
    #     solara.Route("/chat", component=ChatPage, label="Chat"),
    #     solara.Route("/", component=LoginPage, label="Login"),
    # ]

    if not token.value:
        LoginPage()
    elif not thread_id.value:
        ThreadPage()
    else:
        ChatPage()
