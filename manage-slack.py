#!/usr/bin/env python3

import slacker
import requests
import argparse
import datetime
from pprint import pprint
import json
import csv
import os
from slack import WebClient


def parse_args(args=None, parse=True):
    parser = argparse.ArgumentParser(description = 'Manage Slack user activity')
    parser.add_argument('-l', '--list-activity', action = 'store_true', 
                    help = 'print a list of user activity')
    parser.add_argument('-r', '--remove-users', action = 'store_true', 
                        help = 'remove all inactive users from all public channels')

    args = parser.parse_args() if parse else None
    return parser, args


def get_users(users):
    user_report = {}
    for user in users:
        if user['is_bot']:
            continue
        if user['deleted']:
            continue
        user_report[user['real_name']] = { 
            'id': user['id'],
            'time': 0 
            }
    return(user_report)

def users_list(users):
    users_info = {}
    for user in users:
        if user['is_bot']:
            continue
        if user['deleted']:
            continue
        users_info[user['real_name']] = {
            'id': user['id']
        }
    return(users_info)
         

def get_messages(channels, slack_token):  
    message_report = {}  
    message_list = []
    channel_list = []
    for channel in channels:
        messages = channel_history(slack_token, channel['id'])
        if channel['name'] not in channel_list:
            channel_list.append(channel['name'])
        for message in messages:
            if message['type'] == "message" and not "subtype" in message:
                message_report ={
                    'channel': channel['name'],
                    'id': message['user'],
                    'time': float(message['ts'])
                }
                message_list.append(message_report)
    return(message_list)

def message_to_member(message_list, user_dict):
    mes_member_list={}
    for m in message_list:
        for k,v in m.items():
                for k,v in user_dict.items():
                    if m['id'] == v['id']:
                        mes_member_list[k] = m['time']
    return(mes_member_list)


def check_activity(message_list, user_report):
    for m  in message_list:
        for k,v in m.items():
            for k,v in user_report.items():
                if m['id'] == v['id']:
                    if m['time'] > v['time']:
                        v['time'] = m['time']  
                    else:
                        pass
    return(user_report)

# Print report for -l
def report_to_csv(user_report):
    status = []
    for uid, data in user_report.items():
        if data['time'] == 0:
            status.append({
                "member_name": uid,
                "status": "inactive"
            })
        else:
            status.append({
                "member_name": uid,
                "status": "active"
            })
        csv_columns = ['member_name', 'status']
        with open('member_status.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in status:
                writer.writerow(data)

API_METHODS = {
    "users": "users.list",
    "conversations": "conversations.list"
}

def channel_history(token, channel_id):
    url = 'https://slack.com/api/conversations.history/'
    headers = {
        'Content-type': 'application/json'
    }
    params = {
            "token": token,
            "channel": channel_id,
            # "limit": 1,
            "pretty": 1

        }
    r = requests.get(url, headers=headers, params = params)
    data = r.json()
    return(data['messages'])

def slack_api(method,  token):
    url = f'https://slack.com/api/{API_METHODS[method]}'
    headers = {
        'Content-type': 'application/json'
    }
    if method == 'conversations':
        params = {
            "token": token,
            "types": ["public_channel, private_channel"],
            # "limit": 20,
            "pretty": 1

        }
        r = requests.get(url, headers=headers, params = params)
        data = r.json()
        return(data['channels'])
    else:
        params = {
            "token": token,
            # "limit": 1,
            "pretty": 1
        }
        r = requests.get(url, headers=headers, params = params)
        data = r.json()
        return(data['members'])

# Removal, -r
# if args.remove_users:
#     for channel in channels:
#         channel_id = slack.channels.get_channel_id(channel)
#         for uid, data in user_report.items():
#             if data['time'] == 0:
#                 try:
#                     slack.channels.kick(channel=channel_id,user=user_id)
#                 except not_in_channel:
#                     pass

def main():
    _parser, args = parse_args()
    # slack_token = "xoxp-1007626892624-1007668785253-1103928365040-aae685df974363008448e3fc1de3395e"
    slack_token = 'xoxb-1007626892624-1120960962288-AfPLSK9j1PdPS4qmpMxpCuCs'
    oauth_token = 'xoxp-1007626892624-1009836989174-1120937463584-251acb947538d5651f224d2dff8729dc'
    
    if not slack_token:
        print('You need to set the slack_token variable, see the readme file')
        exit()
    if not args.list_activity and not args.remove_users:
        parser.print_help()
        exit()

    # Gather Data
    users = slack_api('users', slack_token)
    channels = slack_api('conversations', slack_token) 

    user_reports = get_users(users)
    user_info = users_list(users)
    messages_list = get_messages(channels, oauth_token)
    # user_to_message = message_to_member(messages_list, user_info)
    updated_users = check_activity(messages_list, user_reports)
    
    if args.list_activity:
        report_to_csv(updated_users)


main()