# Generated by Django 5.0.6 on 2024-06-16 18:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("chat", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="chatthread",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="chatmessage",
            name="thread",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="chat.chatthread"
            ),
        ),
        migrations.AddIndex(
            model_name="chatthread",
            index=models.Index(
                fields=["author", "organization"], name="chat_chatth_author__0b7217_idx"
            ),
        ),
    ]
