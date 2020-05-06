#!/usr/bin/env python3

import slacker
import requests
import argparse
import datetime
from pprint import pprint
from datetime import datetime
import json
import csv
import os
from slack import WebClient
import slack


def parse_args(args=None, parse=True):
    parser = argparse.ArgumentParser(description = 'Manage Slack user activity')
    parser.add_argument('-l', '--list-activity', action = 'store_true', 
                    help = 'print a list of user activity')
    parser.add_argument('-r', '--remove-users', action = 'store_true', 
                        help = 'remove all inactive users from all public channels')
    parser.add_argument('-m', '--member-name', help = 'input member name')
    args = parser.parse_args() if parse else None
    return parser, args

def get_channels(client):
    convos = client.conversations_list(types="public_channel,private_channel")
    channels = []
    for convo in convos:
	    for channel in convo["channels"]:
		    channels.append({
                channel['name']: channel['id']
            })
    return(channels)

def get_users(client):
    user_report = {}
    response = client.users_list()
    users = response["members"]
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

#find specific user
def user(client, member_name):
    user_dict = {}
    response = client.users_list()
    users = response["members"]
    for user in users:
        if user['is_bot']:
            continue
        if user['deleted']:
            continue
        if user['real_name'] == member_name:
            user_dict[user['real_name']] = {
                'id': user['id']
            }
    return(user_dict)


def channel_history(client, channel_id):
    messages = []
    response = client.conversations_history(channel = channel_id)
    convos = response["messages"]
    return(convos)


def get_messages(channels, client):  
    message_report = {}  
    message_list = []
    for channel in channels:
        for k,v in channel.items():
            messages = channel_history(client, v)
            for message in messages:
                if message['type'] == "message" and not "subtype" in message:
                    message_report ={
                        'channel': k,
                        'id': message['user'],
                        'time': float(message['ts'])
                    }
                    message_list.append(message_report)
    return(message_list)


#check presence of specific user
def message_to_member(message_list, user_dict):
    member_messages = []
    latest_message={}
    for m in message_list:
        for k,v in m.items():
                for k,v in user_dict.items():
                    if m['id'] == v['id']:
                        latest_message = {
                            'name': k,
                            'channel': m['channel'],
                            "time" : datetime.fromtimestamp(m['time'])
                        }
                        member_messages.append(latest_message)
    return(member_messages)

#check activity for all users
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
    pprint("Starting script....")
    _parser, args = parse_args()
    oauth_token = 'xoxp-1007626892624-1009836989174-1123151586272-6edac0ac2a32689397b7976eb5d5e76e'
    
    if not oauth_token:
        print('You need to set the oauth_token variable, see the readme file')
        exit()
    if not args.list_activity and not args.remove_users:
        parser.print_help()
        exit()

    client = slack.WebClient(token=oauth_token)
   
    if args.member_name: 
        athlete = user(client, args.member_name)
        pprint("Collecting data for athlete: ")
        pprint(athlete)
        channels = get_channels(client)
        messages_list = get_messages(channels, oauth_token)
        pprint("Here is a list of athlete's messages and timestamps: ")
        last_message = message_to_member(messages_list, athlete)
        pprint("The athlete's most recent message was: ")
        pprint(last_message)

    else:
        pprint("Collecting users...")
        user_reports = get_users(client)
        pprint("Collecting channels...")
        channels = get_channels(client)
        pprint("Collecting messages..")
        messages_list = get_messages(channels, client)
        pprint("Checking member activity..")
        updated_users = check_activity(messages_list, user_reports)

        pprint("Writing to csv file...")
        if args.list_activity:
            report_to_csv(updated_users)

    pprint("Done!")

main()