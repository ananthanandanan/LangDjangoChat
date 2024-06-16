## LangChatDjango

LangChatDjango is a Django-based web application that allows users to chat with an AI-powered chatbot in real-time. Users can join chatrooms and engage in conversations with the chatbot, as well as with other users in the same chatroom.

## Features

- Real-time chat with an AI chatbot
- Multiple chatrooms for group conversations
- User authentication and registration
- Minimalistic but intuitive user interface

## Stack

- Django (Python web framework)
- Django Channels (for real-time communication)
- Django Rest Framework (DRF) with token authentication
- Huey (task queue for background tasks)
- Redis (for caching and message queuing)

## Installation

Follow these steps to install and set up LangChatDjango on your local machine:

1. **Clone the repository**

   ```bash
   git clone https://github.com/ananthanandanan/LangChatDjango.git
   cd LangChatDjango
   ```

2. **Install dependencies**

   ```bash
   poetry install
   ```

3. **Set up the database**

   ```bash
   poetry run python manage.py makemigrations
   poetry run python manage.py migrate
   ```

4. **Start Redis server**

   ```bash
   docker-compose up -d --build
   ```

5. **Start Huey worker**

   ```bash
   poetry run python manage.py run_huey
   ```

6. **Start Django server**
   ```bash
   poetry run python manage.py runserver
   ```

## Usage

Open the browser and go to `http://localhost:8000/chat/register/` to register a new user, then go to `http://localhost:8000/chat/chatroom/` to chat with the bot. If you want to chat with the bot in the same chatroom, open another browser and go to `http://localhost:8000/chat/chatroom/`. As an existing user, you can login at `http://localhost:8000/chat/login/`.
