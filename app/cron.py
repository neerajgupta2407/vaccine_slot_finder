import kronos

from .models import *
from .utils import *

dist_api_response = {}
pincode_api_response = {}
api_obj = APISETU()


def get_resp_by_pincode(pincode):
    if pincode in pincode_api_response:
        return pincode_api_response.get(pincode)
    else:
        resp = api_obj.slot_by_pincode(pincode)
        pincode_api_response[pincode] = resp
        return resp


def get_resp_by_district(d_id):
    if d_id in dist_api_response:
        return dist_api_response.get(d_id)
    else:
        resp = api_obj.slot_by_district(d_id)
        dist_api_response[d_id] = resp
        return resp


@kronos.register("0 */2 * * *")
def reset_counter():
    clients = TelegramAccount.objects.all()
    clients.update(alerts_45=0, alerts_18=0)


@kronos.register("*/5 * * * *")
def send_alerts():
    # Function send out the alerts to user who has subscribed for particular pincode.
    clients = TelegramAccount.objects.filter(is_active=True).exclude(saved_alerts=None)
    for client in clients:
        if not client.saved_alerts:
            continue
        for age, data in client.saved_alerts.items():
            pincodes = data.get(CONST_PINCODES, [])
            district_ids = data.get(CONST_DISTRICT_IDS, [])
            for pincode in pincodes:
                resp = get_resp_by_pincode(pincode)
                notify_to_clients(client, resp, age, pincode=pincode)

            for district_id in district_ids:
                resp = get_resp_by_district(district_id)
                notify_to_clients(client, resp, age, district_id=district_id)


def notify_to_clients(client, centers, age_type, **kwargs):
    eighteen_available = False
    fortyfive_available = False
    if kwargs.get("pincode"):
        st = f"Pincode: {kwargs.get('pincode')}"
    if kwargs.get("district_id"):
        district = Disrtict.objects.get(pk=kwargs.get("district_id"))
        st = f"District: {district.district_name}"
    st = st + f" Age: {age_type}+"
    init_msg = f"<b>We have found a slot for you in {st}.</b>\n"
    if age_type == AgeType._eighteen:
        for cent in centers:
            if cent.is_18_session_available and cent.min_18_slots_available:
                eighteen_available = True
                break
        if eighteen_available:
            notify_clients(
                client=client,
                age_type=AgeType._eighteen,
                centers=[a for a in centers if a.is_18_session_available],
                init_msg_str=init_msg,
            )
    if age_type == AgeType._forty_five:
        for cent in centers:
            if cent.is_45_session_available and cent.min_45_slots_available:
                fortyfive_available = True
                break
        if fortyfive_available:
            notify_clients(
                client=client,
                age_type=AgeType._forty_five,
                centers=[a for a in centers if a.is_45_session_available],
                init_msg_str=init_msg,
            )


def notify_clients(client, centers, age_type, init_msg_str):
    msg = None
    if age_type == AgeType._eighteen and client.alerts_18 < MAX_ALERTS:
        # sending notification to those who has subscribed for 18+
        msg = lis_to_str_with_indx([a.detail_available_18_info_str for a in centers])
        msg = init_msg_str + msg
        client.alerts_18 = client.alerts_18 + 1
        client.total_alerts_18 = client.total_alerts_18 + 1
        client.save()

    elif age_type == AgeType._forty_five and client.alerts_45 < MAX_ALERTS:
        # sending notification to those who has subscribed for 45+
        msg = lis_to_str_with_indx([a.detail_available_45_info_str for a in centers])
        msg = init_msg_str + msg
        client.alerts_45 = client.alerts_45 + 1
        client.total_alerts_45 = client.total_alerts_45 + 1
        client.save()
    if msg:
        msg = append_cowin_link(msg)
        client.send_message(msg)


def send_message_to_all(msg):
    clients = TelegramAccount.objects.filter(is_active=True)
    for client in clients:
        client.send_message(msg)
