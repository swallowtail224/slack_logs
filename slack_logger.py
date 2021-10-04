import os
import json
import csv
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.internal_utils import _next_cursor_is_present

client = WebClient(token='')

member_list = {}
try:
    response = client.users_list()
    members = response.get('members')
    for user in members:
        member_list[user.get('id')] = user.get('real_name')
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")

print(member_list)

'''
try:
    response = client.conversations_history(channel="CNX7VCNBE", limit=200)
    #print(response)
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")


with open('test.json', mode='w', encoding='utf-8') as file:
  json.dump(response.get('messages'), file, ensure_ascii=False, indent=2)
'''

def get_users():
    member_list = {}
    try:
        response = client.users_list()
        members = response.get('members')
        for user in members:
            member_list[user.get('id')] = user.get('name')
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
    return member_list

def get_channel_list(next_cursor=None):
    try:
        response = client.conversations_list(
        types="public_channel", #private_channel",
        cursor = next_cursor
        )
        conversations = response["channels"]
        next = response['response_metadata']['next_cursor']
        print(conversations)
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")
    return conversations, next


def get_channels_id():
    channels, next_cursor = get_channel_list(next_cursor=None)
    while next_cursor:
        conversations, next_cursor = get_channel_list(next_cursor=None)
        channels.extend(conversations)
        if not next_cursor:
            next_cursor == None
            break

    channel_ids = {}
    for channel in channels:
        channel_ids[channel.get('name')] = channel.get('id')
    
    return channel_ids


def get_history(channel_id):
    try:
        response = client.conversations_history(channel=channel_id)
    except SlackApiError as e:
        if e.response["error"] == "ratelimited":
            print('rate limited wait 2 minits.')
            time.sleep(120)
            response = get_history(channel_id)
            return response
        assert e.response["ok"] is False
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")
    return response

def get_tread_history(cahnnel_id, thread_ts):
    print('todo')
    
def get_messages(channel_id, file_path):
    has_more = False
    api_response = get_history(channel_id)
    messages = api_response.get('messages')
    has_more = api_response.get('has_more')
    for message in messages:
        data_type = message.get('type')
        user = message.get('user')
        text = message.get('text')
        timestamp = message.get('ts')
        log = [data_type, user, timestamp, text]
        write_data(file_path, log)
        if 'thread_ts' in message:
            thread_ts = message.get('thread_ts')
            get_tread_history(channel_id, thread_ts)
            print('todo')
    
    while has_more:
        next_cursor = api_response.get('response_metadata').get('next_cursor')
        api_response = get_history(channel_id)
        messages = api_response.get('messages')
        has_more = api_response.get('has_more')

        if not next_cursor:
            has_more = False
            break




def write_data(file_path, log):
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(log)


def main():
    member_list = get_users()
    channel_ids = get_channels_id()