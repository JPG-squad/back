# Generated by Django 4.2 on 2023-05-03 21:38

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("conversation", "0011_alter_answermodel_options_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="answermodel",
            unique_together={("patient", "relevant_point")},
        ),
    ]
