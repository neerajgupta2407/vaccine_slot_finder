# Generated by Django 3.2.2 on 2021-05-08 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TelegramAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("create_time", models.DateTimeField(auto_now_add=True)),
                ("update_time", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("username", models.CharField(blank=True, max_length=30, null=True)),
                ("chat_id", models.CharField(max_length=20)),
                ("registered_18", models.BooleanField(default=False)),
                ("registered_45", models.BooleanField(default=False)),
                ("alerts_18", models.IntegerField(default=0)),
                ("alerts_45", models.IntegerField(default=0)),
            ],
        )
    ]