from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack

import logging

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user(token_key):
    """Get the user associated with the given token key.

    Args:
        token_key (str): The key of the token to retrieve.

    Returns:
        User: The user associated with the token, or an instance of
            `AnonymousUser` if the token is invalid.
    """
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    """Custom token authentication middleware.

    This middleware checks for a token in the query string of the request and
    attempts to authenticate the user with the token. If the token is invalid,
    the user will be set to an instance of `AnonymousUser`.

    NOTE: This middleware should be placed before `AuthMiddlewareStack`. This
    is because `AuthMiddlewareStack` will attempt to authenticate the user
    based on the session data, which is not available for WebSocket
    connections. By placing this middleware first, we can ensure that the user
    is authenticated based on the token before `AuthMiddlewareStack` is
    invoked.

    Reference: https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
    """

    async def __call__(self, scope, receive, send):
        try:
            token_key = dict(
                (x.split("=") for x in scope["query_string"].decode().split("&"))
            ).get("token", None)
        except ValueError:
            token_key = None
        scope["user"] = (
            AnonymousUser() if token_key is None else await get_user(token_key)
        )

        logger.debug(
            f"User authenticated with token: {scope['user']}, token_key: {token_key}"
        )

        return await super().__call__(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
