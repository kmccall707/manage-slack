#!/usr/bin/env python3

import slacker
import argparse
import datetime
from pprint import pprint
import json
import csv


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

def get_messages(channels, slack):  
    message_report = {}  
    message_list = []
    for channel in channels:
        response = slack.channels.history(channel['id'])
        messages = response.body['messages']
        for message in messages:
            if message['type'] == "message" and not "subtype" in message:
                message_report ={
                    'id': message['user'],
                    'time': float(message['ts'])
                }
                message_list.append(message_report)
    return(message_list)

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
    slack_token = "xoxp-1007626892624-1007668785253-1062648276807-f28c657a2a81ad6f2472a29dae5909d3"

    if not slack_token:
        print('You need to set the slack_token variable, see the readme file')
        exit()
    if not args.list_activity and not args.remove_users:
        parser.print_help()
        exit()

    # Gather Data
    slack = slacker.Slacker(token=slack_token) 
    response = slack.users.list()
    users = response.body['members']
    response = slack.channels.list()
    channels = response.body['channels']

    user_reports = get_users(users)
    messages_list = get_messages(channels, slack)
    updated_users = check_activity(messages_list, user_reports)
    
    if args.list_activity:
        report_to_csv(updated_users)


main()