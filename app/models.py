# Create your models here.
from decouple import config
from django.db import models

from apis.apisetu.apisetu import APISETU
from app.utils import *
from vaccine_slots.settings import telegram_bot

MAX_ALERTS = config("max_alerts")
SHOW_LAST_N_SEARCH = 3

CONST_DISTRICT_IDS = "district_ids"
CONST_PINCODES = "pincodes"


class AgeType:
    _forty_five = "45"
    _eighteen = "18"


class States(models.Model):
    state_id = models.IntegerField(primary_key=True)
    state_name = models.CharField(max_length=100)

    @classmethod
    def sync(cls):
        setu_obj = APISETU()
        states = setu_obj.get_states()
        objs = [cls(state_id=a.state_id, state_name=a.state_name) for a in states]
        cls.objects.bulk_create(objs)

    def __str__(self):
        return f"States <{self.state_id}: {self.state_name}>"


class Disrtict(models.Model):
    district_id = models.IntegerField(primary_key=True)
    district_name = models.CharField(max_length=100)
    state = models.ForeignKey(States, on_delete=models.CASCADE)

    def __str__(self):
        return f"District <{self.district_id}: {self.district_name}>"

    @classmethod
    def sync(cls):
        setu_obj = APISETU()
        for state in States.objects.all():
            districts = setu_obj.get_district(state.pk)
            objs = [
                cls(
                    district_id=a.district_id,
                    district_name=a.district_name,
                    state_id=state.pk,
                )
                for a in districts
            ]
            cls.objects.bulk_create(objs)


class TelegramAccount(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=30, null=True, blank=True)
    chat_id = models.CharField(max_length=20)
    pincode = models.IntegerField(default=0)

    # saved_alerts = {'45': {'district_ids': [-2017859857], 'pincodes': ['110027']}, '18': {'district_ids': [-2017859857], 'pincodes': ['110028', '110027']}}
    saved_alerts = models.JSONField(null=True)

    recent_searches = models.JSONField(null=True)
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

    def save_search_query(self, query):
        self.recent_searches = self.recent_searches or []
        self.recent_searches = insert_top(self.recent_searches, query)
        self.save()

    def get_recent_searches(self, last_n_searches=SHOW_LAST_N_SEARCH):
        lis = self.recent_searches or []
        return lis[:last_n_searches]

    def alert(self, age_type, **kwargs):
        district_id = kwargs.get("district_id")
        pincode = kwargs.get("pincode")
        dic = self.saved_alerts or {}
        dic[age_type] = dic.get(age_type, {})
        if district_id:
            dic[age_type][CONST_DISTRICT_IDS] = dic[age_type].get(
                CONST_DISTRICT_IDS, []
            )
            dic[age_type][CONST_DISTRICT_IDS] = insert_top(
                dic[age_type][CONST_DISTRICT_IDS], district_id
            )

        if pincode:
            dic[age_type][CONST_PINCODES] = dic[age_type].get(CONST_PINCODES, [])
            dic[age_type][CONST_PINCODES] = insert_top(
                dic[age_type][CONST_PINCODES], pincode
            )
        self.saved_alerts = dic
        self.alerts_18 = 0
        self.alerts_45 = 0
        self.save()
        st = f"We will notify you when slots will be available for age {age_type} in "
        if district_id:
            d = Disrtict.objects.get(pk=district_id)
            st += f"{d.district_name}"
        if pincode:
            st += f"Pincode {pincode}"
        return st

    @classmethod
    def subscribed_data(cls):
        objs = cls.objects.filter(is_active=True)
        pincodes = []
        district_ids = []
        for obj in objs:
            if obj.saved_alerts:
                for k, v in obj.saved_alerts.items():
                    pincodes.extend(v.get(CONST_PINCODES, []))
                    district_ids.extend(v.get(CONST_DISTRICT_IDS, []))

        return {
            CONST_PINCODES: list(set(pincodes)),
            CONST_DISTRICT_IDS: list(set(district_ids)),
        }

    def get_subscribed_data(self):
        pincodes = []
        district_ids = []
        if self.saved_alerts:
            for k, v in self.saved_alerts.items():
                pincodes.extend(v.get(CONST_PINCODES, []))
                district_ids.extend(v.get(CONST_DISTRICT_IDS, []))

        return {
            CONST_PINCODES: list(set(pincodes)),
            CONST_DISTRICT_IDS: list(set(district_ids)),
        }
