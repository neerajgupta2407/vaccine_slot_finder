#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and alerted at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
# Enable logging
import logging

from decouple import config
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater

from apis.apisetu.apisetu import APISETU
from app.models import AgeType, Disrtict, States, TelegramAccount

from .utils import *

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


SEARCH_FORMAT = "Please Enter `Age pincode` \n\tEg: 22 110027"
alert_format = "Please Enter `alert Age pincode` for getting alert on slot availability.\n\tEg: alert 22 110027"


class Operation:
    search = "search"
    alert = "alert"

    @classmethod
    def get_name(cls, st):
        for a in [cls.search, cls.alert]:
            if st in a:
                return a


class QueryFilter:
    command: str
    age: int = 0
    pincode: int = 0
    delim = " "

    def __init__(self, query_str):
        self.str = remove_extra_delimiter(query_str, self.delim)
        query_lis = self.str.split(self.delim)
        assert len(query_lis) >= 2, SEARCH_FORMAT
        try:
            self.age = int(query_lis[0])
            self.pincode = int(query_lis[1])
            self.operation = Operation.search
        except:
            self.operation = Operation.get_name(query_lis[0])
            self.age = int(query_lis[1])
            self.pincode = int(query_lis[2])

        assert self.age > 0, "Invalid Age"
        assert self.pincode > 0, "Invalid pincode"


class Commands:
    available_slot_18 = "available_slot_18"
    available_slot_45 = "available_slot_45"
    alert_for_18 = "alert for 18+"
    alert_for_45 = "alert for 45+"
    list_states = "List States"
    help = "help"
    start = "start"


def slots_str_by_lis(data, age_type, error_msg="No Slots available"):
    reply_text = error_msg
    if age_type == AgeType._forty_five:
        resp = [a for a in data if a.is_45_session_available]
        if len(resp) > 0:
            reply_text = lis_to_str_with_indx(
                [a.detail_available_45_info_str for a in resp]
            )
    elif age_type == AgeType._eighteen:
        resp = [a for a in data if a.is_18_session_available]
        if len(resp) > 0:
            reply_text = lis_to_str_with_indx(
                [a.detail_available_18_info_str for a in resp]
            )
    return reply_text


def command_handler(update: Update, context: CallbackContext) -> None:
    state_pretext = "State:"
    district_pretext = "District:"
    slot_18_pretext = "18+ Slot in "
    slot_45_pretext = "45+ Slot in "
    api_obj = APISETU()
    text = update.message.text
    tele_id = update.message.chat_id
    bot_name = context.bot.username
    username = update.message.from_user.full_name
    tele = TelegramAccount.subscribe(tele_id, username)
    user_info = {}
    reply_text = "Invalid command"
    reply_keyboard = [
        ["18 110027", "45 110027"],
        ["alert 18 110027", "alert 45 110027"],
        [Commands.list_states],
        [Commands.help],
    ]
    if text in [Commands.start, Commands.help, "/start"]:
        lis = [SEARCH_FORMAT, alert_format]
        reply_text = lis_to_str_with_indx(lis)
    elif text == Commands.list_states:
        states = States.objects.all().order_by("state_name")
        reply_text = "Here is the list of States"
        reply_keyboard = [[state_pretext + a.state_name] for a in states]
    elif text.startswith(state_pretext):
        state_name = text.replace(state_pretext, "")
        disticts = Disrtict.objects.filter(state__state_name=state_name).order_by(
            "district_name"
        )
        reply_text = f"Here is the list of District for State: {state_name}"
        reply_keyboard = [[district_pretext + a.district_name] for a in disticts]

    elif text.startswith(district_pretext):
        district_name = text.replace(district_pretext, "")
        district = Disrtict.objects.get(district_name=district_name)
        reply_text = f"Please select below option"
        reply_keyboard = [
            [slot_18_pretext + district.district_name],
            [slot_45_pretext + district.district_name],
        ]

    elif text.startswith(slot_18_pretext):
        district_name = text.replace(slot_18_pretext, "")
        district = Disrtict.objects.get(district_name=district_name)
        data = api_obj.slot_by_district(district.pk)
        reply_text = slots_str_by_lis(
            data,
            AgeType._eighteen,
            error_msg=f"No Slots Available for Age: 18+ in district: {district_name}",
        )

    elif text.startswith(slot_45_pretext):
        district_name = text.replace(slot_45_pretext, "")
        district = Disrtict.objects.get(district_name=district_name)
        data = api_obj.slot_by_district(district.pk)
        reply_text = slots_str_by_lis(
            data,
            AgeType._forty_five,
            error_msg=f"No Slots Available for Age: 45+ in district: {district_name}",
        )

    else:
        try:
            obj = QueryFilter(text)
            pincode = obj.pincode
            age = obj.age
            operation = obj.operation
            if operation == Operation.alert:
                if Commands.alert_for_18 == text or age < 44:
                    reply_text = tele.alert(pincode, 18)
                elif Commands.alert_for_45 == text or age > 44:
                    reply_text = tele.alert(pincode, 45)
            else:
                if Commands.available_slot_18 in text or age < 44:
                    data = api_obj.slot_by_pincode(pincode)
                    reply_text = slots_str_by_lis(
                        data,
                        AgeType._eighteen,
                        error_msg=f"No Slots Available for Age: {age} in pincode: {pincode}",
                    )

                elif Commands.available_slot_45 in text or age > 44:
                    data = api_obj.slot_by_pincode(pincode)
                    reply_text = slots_str_by_lis(
                        data,
                        AgeType._forty_five,
                        error_msg=f"No Slots Available for Age: {age} in pincode: {pincode}",
                    )

        except Exception as e:
            reply_text = str(e)
    update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    token = config("telegram_bot_key")
    updater = Updater(token, use_context=True)
    # Get the dispatcher to alert handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(MessageHandler(Filters.text, command_handler))
    # on noncommand i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
