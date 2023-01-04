"""
Classes for the data stored in Notion
"""

from datetime import datetime
from typing import Any, Optional
import calendar
import locale

DD_MM_YY_FORMAT = "%d/%m/%y"

locale.setlocale(locale.LC_ALL, "es_ES.UTF8")


class DateRange:
    """Class representing a period of time between two dates, or a single date."""

    def __init__(self, start: datetime, end: Optional[datetime]):
        """
        Initializes a new DateRange
        :param start: Date in which the range begins
        :param end: Date in which the range ends. Can be none for a single date.
        """
        if not start:
            raise ValueError("Cannot create a DateRange without a start date")
        if end and start > end:
            raise ValueError("End date cannot be before start date")

        self.start = start
        self.end = end

    @staticmethod
    def get_weekday_name(day: int) -> str:
        """
        Return the name of a weekday in the configured locale
        :param day: Number of the day of the week, from 0 to 6 (inclusive)
        :return: String with the weekday name
        """
        try:
            return calendar.day_name[day]
        except KeyError:
            raise ValueError("Weekday must be 0 <= n < 7")

    @staticmethod
    def get_month_name(month: int) -> str:
        """
        Return the name of a month in the configured locale
        :param month: Number of the month, from 1 to 12 (inclusive)
        :return: String with the month name
        """
        try:
            return calendar.month_name[month]
        except KeyError:
            raise ValueError("Month must be 1 <= n < 13")

    def get_date_description(self, date: datetime):
        """
        Return a text description of a date in the configured locale
        :param date: Datetime object for the date to describe
        :return: String with the date description
        """
        return (
            f"{self.get_weekday_name(date.weekday())} {date.day} "
            f"de {self.get_month_name(date.month)}"
        )

    def __str__(self):
        """
        Returns a user-friendly representation for the DateRange in the configured
        locale
        :return: String with the representation
        """
        if not self.end:
            return f"El {self.get_date_description(self.start)}"
        return (
            f"Del {self.get_date_description(self.start)} "
            f"al {self.get_date_description(self.end)}"
        )

    def __repr__(self):
        """
        Returns a dev-friendly representation for the DateRange in the configured
        locale
        :return: String with the representation
        """
        if not self.end:
            return self.start.strftime(DD_MM_YY_FORMAT)
        return (
            f"{self.start.strftime(DD_MM_YY_FORMAT)}"
            f"->{self.end.strftime(DD_MM_YY_FORMAT)}"
        )


class NotionEvent:
    """Class representing a calendar event retrieved from Notion"""

    def __init__(
        self,
        title: str,
        date: DateRange,
        event_type: str,
        location: str,
        scouters: [str],
        participant_num: int,
        url: str,
    ):
        """
        Initializes a new NotionEvent instance
        :param title: Title for the event
        :param date: Date for the event
        :param event_type: Type for the event
        :param location: Location for the event
        :param scouters: List with the names of the attending scouters
        :param participant_num: Number of non-scouter participants
        :param url: URL for the event in Notion
        """
        self.title = title
        self.date = date
        self.type = event_type
        self.location = location
        self.scouters = scouters
        self.participant_num = participant_num
        self.url = url

    @classmethod
    def from_page(cls, page: Any):
        """
        Initializes a new NotionEvent instance from a Notion page
        :param page: Dictionary with the Notion page data
        """
        properties = page["properties"]

        title = properties["Name"]["title"][0]["plain_text"]

        try:
            location = properties["Lugar"]["rich_text"][0]["plain_text"]
        except IndexError:
            location = ""

        date_begin = properties["Fecha"]["date"]["start"]
        date_end = properties["Fecha"]["date"]["end"]

        date_begin_parsed = datetime.fromisoformat(date_begin)
        date_end_parsed = datetime.fromisoformat(date_end) if date_end else None

        date_range = DateRange(date_begin_parsed, date_end_parsed)

        event_type = properties["Tipo"]["select"]["name"]

        scouters = [
            scouter["name"]
            for scouter in properties["Scouters asistentes"]["multi_select"]
        ]

        participant_num = len(properties["Educandos asistentes"]["relation"])

        url = page["url"]

        return cls(
            title, date_range, event_type, location, scouters, participant_num, url
        )

    def __repr__(self):
        return (
            f"<NotionEvent title='{self.title}', date=[{repr(self.date)}], "
            f"type='{self.type}', location='{self.location}'>"
        )
