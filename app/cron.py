import kronos

from apis.apisetu.apisetu import APISETU

from .models import AgeType, TelegramAccount
from .utils import *


@kronos.register("*/10 * * * *")
def send_alerts():
    # Function send out the alerts to user who has subscribed for particular pincode.

    pincodes = (
        TelegramAccount.objects.filter(is_active=True)
        .values_list("pincode", flat=True)
        .distinct()
    )
    api_obj = APISETU()
    eighteen_available = False
    fortyfive_available = False
    for pincode in pincodes:
        resp = api_obj.slot_by_pincode(pincode)
        for cent in resp:
            if cent.is_18_session_available:
                eighteen_available = True
            if cent.is_45_session_available:
                fortyfive_available = True

        if eighteen_available:
            notify_clients(
                age_type=AgeType._eighteen,
                centers=[a for a in resp if a.is_18_session_available],
            )
        if fortyfive_available:
            notify_clients(
                age_type=AgeType._forty_five,
                centers=[a for a in resp if a.is_45_session_available],
            )


def notify_clients(centers, age_type):
    init_str = "We have found a slot for you.\n"
    if age_type == AgeType._eighteen:
        # sending notification to those who has subscribed for 18+
        msg = lis_to_str_with_indx([a.detail_available_18_info_str for a in centers])
        msg = init_str + msg
        account = TelegramAccount.registered_18_plus()
        for a in account:
            a.alerts_18 = a.alerts_18 + 1
            a.save()
            a.send_message(msg)

    elif age_type == AgeType._forty_five:
        # sending notification to those who has subscribed for 45+
        msg = lis_to_str_with_indx([a.detail_available_45_info_str for a in centers])
        account = TelegramAccount.registered_45_plus()
        for a in account:
            msg = init_str + msg
            a.alerts_45 = a.alerts_45 + 1
            a.save()
            a.send_message(msg)
