#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def lis_to_str_with_indx(lis):
    return "\n".join([f"{idx + 1}. {b}" for idx, b in enumerate(lis)])


def lis_to_str(lis):
    return "\n".join([f"{b}" for idx, b in enumerate(lis)])


class Commands:
    available_slot_18 = "available_slot_18"
    available_slot_45 = "available_slot_45"


def command_handler(update: Update, context: CallbackContext) -> None:
    api_obj = APISETU()
    text = update.message.text
    tele_id = update.message.chat_id
    bot_name = context.bot.username
    username = update.message.from_user.full_name
    user_info = {}
    reply_text = "Invalid command"
    reply_keyboard = [[Commands.available_slot_18, Commands.available_slot_45]]
    if Commands.available_slot_18 in text:
        pincode = 110027
        data = api_obj.slot_by_pincode(pincode)
        resp = [a for a in data if a.is_18_session_available]
        if len(resp) > 0:
            reply_text = lis_to_str_with_indx(
                [a.detail_available_18_info_str for a in resp]
            )
        else:
            reply_text = "No Slots Available"

    elif Commands.available_slot_45 in text:
        pincode = 110027
        data = api_obj.slot_by_pincode(pincode)
        resp = [a for a in data if a.is_45_session_available]
        if len(resp) > 0:
            reply_text = lis_to_str_with_indx(
                [a.detail_available_45_info_str for a in resp]
            )

        else:
            reply_text = "No Slots Available"

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
    # Get the dispatcher to register handlers
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
