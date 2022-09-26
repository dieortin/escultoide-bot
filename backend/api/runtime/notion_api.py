import os
from datetime import datetime

import boto3

from notion_client import Client

# Get environment variables
CALENDAR_DB_ID = os.environ["NotionCalendarID"]
NOTION_SECRET_NAME = os.environ["NotionSecretName"]

secrets_manager = boto3.client("secretsmanager")
NOTION_API_KEY = secrets_manager.get_secret_value(SecretId=NOTION_SECRET_NAME)[
    "SecretString"
]

notion = Client(auth=NOTION_API_KEY)


def get_next_event_after(date: datetime):
    date_as_text = date.isoformat()
    query_res = notion.databases.query(
        **{
            "database_id": CALENDAR_DB_ID,
            "filter": {"property": "Fecha", "date": {"after": date_as_text}},
            "sorts": [{"property": "Fecha", "direction": "ascending"}],
        }
    )

    return query_res["results"][0]


def get_next_event():
    return get_next_event_after(datetime.utcnow())


def get_next_event_description() -> str:
    next_event = get_next_event()
    return describe_event(next_event)


def describe_event(event: dict) -> str:
    event_props = event["properties"]

    title = event_props["Name"]["title"][0]["plain_text"]
    place = event_props["Lugar"]["rich_text"][0]["plain_text"]

    date = event_props["Fecha"]["date"]["start"]
    date = datetime.fromisoformat(date)

    weekday_name = get_weekday_name(date.weekday())
    month_name = get_month_name(date.month)
    return f"{title}, en {place} el {weekday_name} {date.day} de {month_name}"


def describe_attending_scouters(event: dict) -> str:
    prop = event["properties"]["Scouters asistentes"]["multi_select"]
    scouter_list = [scouter["name"] for scouter in prop]

    if not scouter_list:
        return "Ninguno"
    else:
        return ", ".join(scouter_list)


def get_weekday_name(day: int) -> str:
    weekdays = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
    ]
    return weekdays[day]


def get_month_name(month: int) -> str:
    months = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    return months[month - 1]
