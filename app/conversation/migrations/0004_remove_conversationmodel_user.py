# Generated by Django 4.2 on 2023-04-29 17:42

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("conversation", "0003_conversationmodel_conversation"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="conversationmodel",
            name="user",
        ),
    ]
