import configparser
import json
from datetime import datetime

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)


filename = 'channel_messages.json'

config = configparser.ConfigParser()
config.read("config.ini")

api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

client = TelegramClient(username, api_id, api_hash)

entity = config['Telegram']['channel']


async def request_news():
    await client.start()
    # Ensure you're authorized
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 1000
    all_messages = []
    total_messages = 0
    total_count_limit = 10000

    while True:
        print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    all_message_details = []

    for message in all_messages:
        if 'message' in message.keys():
            all_message_details.append({"id": message['id'], "date": message['date'], "message": message['message']})

    with open(filename, 'w') as outfile:
        json.dump(all_message_details, outfile, indent=4, cls=DateTimeEncoder)


async def update_news():
    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 20
    all_messages = []

    history = await client(GetHistoryRequest(
        peer=my_channel,
        offset_id=offset_id,
        offset_date=None,
        add_offset=0,
        limit=limit,
        max_id=0,
        min_id=0,
        hash=0
    ))

    if not history.messages:
        return

    messages = history.messages
    for message in messages:
        all_messages.append(message.to_dict())

    all_message_details = []

    with open(filename, 'r') as f:
        json_messages = json.load(f)
        for message in all_messages:
            if 'message' in message.keys():
                for msg in json_messages:
                    if msg.get('id') == message['id']:
                        return
                all_message_details.append(
                    {"id": message['id'], "date": message['date'], "message": message['message']})

    with open(filename, 'r+') as file:
        json_messages = json.load(file)
        update_messages = all_message_details + json_messages

        json.dump(update_messages, file, indent=4, cls=DateTimeEncoder)

# with client:
#     client.loop.run_until_complete(request_news())
