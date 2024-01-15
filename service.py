from datetime import datetime, timezone, timedelta
import locale
from itertools import islice
import json

file_path = 'channel_messages.json'


def get_news(amount: int) -> list:
    objects = __read_objects(amount)
    messages = []

    for obj in objects:
        message = obj['message'] + "\n\n" + __format_datetime(obj['date'])
        messages.append(message)

    return messages


def get_news_by_keyword(keyword: str) -> list:
    objects = __find_by_keyword(keyword)
    messages = []

    for obj in objects:
        message = obj['message'] + "\n\n" + __format_datetime(obj['date'])
        messages.append(message)

    return messages


def __format_datetime(datetime_str):
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

    dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S%z")

    dt_msk = dt.astimezone(timezone.utc).astimezone(timezone(timedelta(hours=3)))

    formatted_date = dt_msk.strftime("%d %B")
    formatted_time = dt_msk.strftime("%H:%M")

    formatted_datetime = f"{formatted_date} в {formatted_time} МСК"

    return formatted_datetime


def __find_by_keyword(keyword: str) -> list:
    objects = []
    limit = 10
    with open(file_path, 'r') as file:
        json_objects = json.load(file)
        for o in json_objects:
            if keyword in o['message']:
                objects.append(o)
            if len(objects) == limit:
                break
    return objects


def __read_objects(amount: int) -> list:
    objects = []
    with open(file_path, 'r') as file:
        json_objects = json.load(file)
        for o in json_objects:
            if len(o['message']) > 0:
                objects.append(o)
            if len(objects) == amount:
                break
    return objects

