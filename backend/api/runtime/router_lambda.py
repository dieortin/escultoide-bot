import functools
import json
import os
import asyncio
from typing import Callable, Any, Coroutine

import boto3
from telegram.ext import Application, CommandHandler
from telegram import Update
from notion.api import get_next_event

ALLOWED_USERNAMES = set(os.environ["AllowedUsers"].split(","))
TELEGRAM_SECRET_NAME = os.environ["TelegramSecretName"]

secrets_manager = boto3.client("secretsmanager")
TELEGRAM_API_KEY = secrets_manager.get_secret_value(SecretId=TELEGRAM_SECRET_NAME)[
    "SecretString"
]

application = Application.builder().token(TELEGRAM_API_KEY).build()


def status_code(code: int) -> dict:
    return {"statusCode": code}


def authorized_users_only(func: Callable[[Update, Any], Coroutine[Any, Any, None]]):
    @functools.wraps(func)
    async def wrapper_authorized_users_only(update: Update, context: Any):
        message_username = update.message.from_user.username

        if message_username not in ALLOWED_USERNAMES:
            print(
                f"User {message_username} not authorized for function "
                f"{func.__name__}"
            )
            return status_code(401)
        await func(update, context)

    return wrapper_authorized_users_only


async def echo_callback(update: Update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    text = update.message.text

    message = f"Received message from {user} in chat {chat_id}:" f"\n{text}"
    await update.message.reply_text(message)


@authorized_users_only
async def proximo_callback(update: Update, context):
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

    await update.message.reply_html(response_message, disable_web_page_preview=True)
    print(f"Sent response: <{response_message}>")


# Add message and command handlers
application.add_handler(CommandHandler("echo", echo_callback))
application.add_handler(CommandHandler("proximo", proximo_callback))

async def handle_update(update: Update):
    if update.message:
        print(
            f"Received message from {update.message.from_user}:"
            f"\n{update.message.text}"
        )
    async with application:
        await application.process_update(update)


def handler(event, context):
    print("Received new update from webhook")
    update = Update.de_json(event, application.bot)
    if not update:
        raise ValueError(f"Received event is not a valid Telegram update, event is {json.dumps(event, indent=2)}")
    
    asyncio.run(handle_update(update))
    return status_code(200)
