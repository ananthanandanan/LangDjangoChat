from django.contrib import admin

# Register your models here.
from .models import ChatThread, ChatMessage

admin.site.register(ChatThread)
admin.site.register(ChatMessage)
