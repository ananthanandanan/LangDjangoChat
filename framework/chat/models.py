from django.db import models
import uuid
from django.conf import settings


# Create your models here.
class ChatThread(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=["author", "organization"]),
        ]

    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    SENDER_TYPES = [
        ("U", "User"),
        ("B", "Bot"),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE)
    content = models.TextField()
    sender = models.CharField(max_length=1, choices=SENDER_TYPES, default="U")
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def sender_enum(self):
        return dict(self.SENDER_TYPES).get(self.sender)

    def __str__(self):
        return self.content
