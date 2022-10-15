import os
from datetime import datetime
from typing import Any

import boto3

from notion_client import Client
from .model import NotionEvent

# Get environment variables
CALENDAR_DB_ID = os.environ["NotionCalendarID"]
NOTION_SECRET_NAME = os.environ["NotionSecretName"]

secrets_manager = boto3.client("secretsmanager")
NOTION_API_KEY = secrets_manager.get_secret_value(SecretId=NOTION_SECRET_NAME)[
    "SecretString"
]

notion = Client(auth=NOTION_API_KEY)


def get_pages_after(date: datetime) -> [Any]:
    """
    Fetch the Notion pages with a date after the provided one
    :param date: Date to use as a filter
    :return: List with dictionaries for the Notion pages
    """
    date_as_text = date.isoformat()
    query_res = notion.databases.query(
        **{
            "database_id": CALENDAR_DB_ID,
            "filter": {"property": "Fecha", "date": {"after": date_as_text}},
            "sorts": [{"property": "Fecha", "direction": "ascending"}],
        }
    )

    return query_res["results"]


def get_events_after(date: datetime) -> [NotionEvent]:
    """
    Return the Notion events with a date after the provided one
    :param date: Date to use as a filter
    :return: List with NotionEvent objects
    """
    pages = get_pages_after(date)

    return [NotionEvent.from_page(page) for page in pages]


def get_next_event_after(date: datetime) -> NotionEvent:
    """
    Return the first Notion event with a date after the provided one
    :param date: Date to use as a filter
    :return: NotionEvent object
    """
    return NotionEvent.from_page(get_pages_after(date)[0])


def get_next_event() -> NotionEvent:
    """
    Return the first Notion event with a date after the current one
    :return: NotionEvent object
    """
    return get_next_event_after(datetime.utcnow())
