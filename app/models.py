# Create your models here.
from decouple import config
from django.db import models

from vaccine_slots.settings import telegram_bot

MAX_ALERTS = config("max_alerts")


class AgeType:
    _forty_five = 45
    _eighteen = 18


class TelegramAccount(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=30, null=True, blank=True)
    chat_id = models.CharField(max_length=20)
    pincode = models.IntegerField(default=0)
    registered_18 = models.BooleanField(default=False)
    registered_45 = models.BooleanField(default=False)
    alerts_18 = models.IntegerField(default=0)
    alerts_45 = models.IntegerField(default=0)

    def send_message(self, msg):
        telegram_bot.send_message(chat_id=self.chat_id, text=msg)

    @classmethod
    def subscribe(cls, chat_id, username, meta_info={}):
        """
        Subsribes To telegram.
        :param chat_id:
        :param bot_name:
        :return:
        """
        obj, _ = cls.objects.get_or_create(chat_id=chat_id)
        obj.username = username[:28]
        obj.meta_info = meta_info
        obj.save()
        return obj

    @classmethod
    def unsubscribe(cls, chat_id, bot_name):
        """
        UnSubsribes To telegram.
        :param chat_id:
        :param bot_name:
        :return:
        """
        cls.objects.filter(chat_id=chat_id, bot_name=bot_name).update(is_active=False)
        return True

    def alert(self, pincode, age):
        text = f"Age:{age}. Pincode: {pincode}. "
        if age < 45:
            self.alerts_18 = 0  # resetting the alerts count.
            if self.registered_18:
                text = text + "Already registered"
            else:
                self.registered_18 = True
                text = text + f"Registered Successfully"
        else:
            self.alerts_45 = 0  # resetting the alerts count.
            if self.registered_45:
                text = text + "Already registered"
            else:
                self.registered_45 = True
                text = text + "Registered Successfully."
        self.pincode = pincode
        self.save()
        return text

    @classmethod
    def registered_45_plus(cls):
        return cls.objects.filter(
            is_active=True, registered_45=True, alerts_45__lte=MAX_ALERTS
        )

    @classmethod
    def registered_18_plus(cls):
        return cls.objects.filter(
            is_active=True, registered_18=True, alerts_18__lte=MAX_ALERTS
        )
