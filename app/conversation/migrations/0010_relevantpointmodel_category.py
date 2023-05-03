# Generated by Django 4.2 on 2023-05-03 18:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("conversation", "0009_ephemeralanswermodel"),
    ]

    operations = [
        migrations.AddField(
            model_name="relevantpointmodel",
            name="category",
            field=models.CharField(
                choices=[("PERSONAL", "personal"), ("SALUD", "salud")],
                default="personal",
                max_length=20,
            ),
        ),
    ]
