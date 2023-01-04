import functools
import json
import os
from typing import Callable, Any
from queue import Queue

import boto3
from telegram.ext import Dispatcher, CommandHandler
from telegram import Update, Bot
from notion.api import get_next_event

ALLOWED_USERNAMES = set(os.environ["AllowedUsers"].split(","))
TELEGRAM_SECRET_NAME = os.environ["TelegramSecretName"]

secrets_manager = boto3.client("secretsmanager")
TELEGRAM_API_KEY = secrets_manager.get_secret_value(SecretId=TELEGRAM_SECRET_NAME)[
    "SecretString"
]

bot = Bot(token=TELEGRAM_API_KEY)
dispatcher = Dispatcher(bot, Queue(), use_context=True)


def status_code(code: int) -> dict:
    return {"statusCode": code}


def authorized_users_only(func: Callable[[Update, Any], None]):
    @functools.wraps(func)
    def wrapper_authorized_users_only(update: Update, context: Any):
        message_username = update.message.from_user.username

        if message_username not in ALLOWED_USERNAMES:
            print(
                f"User {message_username} not authorized for function "
                f"{func.__name__}"
            )
            return status_code(401)
        return func(update, context)

    return wrapper_authorized_users_only


def echo_callback(update: Update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    text = update.message.text

    message = f"Received message from {user} in chat {chat_id}:" f"\n{text}"
    update.message.reply_text(message)


@authorized_users_only
def proximo_callback(update: Update, context):
    next_event = get_next_event()

    participants_str = (
        f"\n\N{baby angel} <b>{next_event.participant_num}</b> educandos"
        if next_event.participant_num > 0 else ""
    )

    scouters_word = "scouter" if len(next_event.scouters) == 1 else "scouters"
    scouters_str = f"\n\N{mage} <b>{len(next_event.scouters)}</b> {scouters_word}"
    if next_event.scouters:
        scouters_str += f": <i>{', '.join(next_event.scouters)}</i>"

    response_message = (
        f"\n<u><b>{next_event.title}</b></u>"
        f"\n\N{stopwatch} {next_event.date}"
        f"\n\N{pushpin} {next_event.location}"
        f"{participants_str}"
        f"{scouters_str}"
        f"\n<a href='{next_event.url}'>Ver en Notion</a>"
    )

    update.message.reply_html(response_message, disable_web_page_preview=True)
    print(f"Sent response: <{response_message}>")


# Add message and command handlers
dispatcher.add_handler(CommandHandler("echo", echo_callback))
dispatcher.add_handler(CommandHandler("proximo", proximo_callback))


def handler(event, context):
    print("Received new update from webhook")
    update = Update.de_json(event, bot)
    if not update:
        print("Received event doesn't seem to be a valid Telegram update")
        print(f"Event is: {json.dumps(event, indent=2)}")
        return status_code(400)

    if update.message:
        print(
            f"Received message from {update.message.from_user}:"
            f"\n{update.message.text}"
        )

    try:
        dispatcher.process_update(update)
    except Exception as e:
        print(f"Exception happened while processing update: {e}")
        return status_code(500)

    return status_code(200)
