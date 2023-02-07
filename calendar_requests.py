import datetime
import os.path
import unicodedata
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = "fd5c6ef22a216acd764d766347a1bcf0019ceadb8152137ae0a4744bb7707228@group.calendar.google.com"


def get_today_events(max=15):

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        today_date = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S.%fZ')
        start_of_today = (datetime.datetime(year = today_date.year, month = today_date.month, day = today_date.day, hour = 0, minute = 1)).isoformat()+ 'Z'  # 'Z' indicates UTC time
        esiee_calendar_id = 'fd5c6ef22a216acd764d766347a1bcf0019ceadb8152137ae0a4744bb7707228@group.calendar.google.com'
        events_result = service.events().list(calendarId=esiee_calendar_id, timeMin=start_of_today,
                                              maxResults=max, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        # do stuff here
        today_events = []
        for event in events:
            event_day = (datetime.datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')).day
            today = (datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S.%fZ')).day

            if (event_day == today):
                today_events.append(event)

        return today_events
        
    except HttpError as error:
        print('An error occurred: %s' % error)
        return ([])


def get_next_events(max=10, istoday=False):

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        today_date = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S.%fZ')
        esiee_calendar_id = 'fd5c6ef22a216acd764d766347a1bcf0019ceadb8152137ae0a4744bb7707228@group.calendar.google.com'
        events_result = service.events().list(calendarId=esiee_calendar_id, timeMin=now,
                                              maxResults=max, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        # do stuff here
        today_events = []
        for event in events:
            if istoday == True:
                event_day = (datetime.datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')).day
                today = (datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S.%fZ')).day

                if (event_day == today):
                    today_events.append(event)
            else:
                today_events.append(event)

        return today_events
        
    except HttpError as error:
        print('An error occurred: %s' % error)
        return ([])




def get_tomorrow_events(max=15):

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        today_date = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S.%fZ')
        tomorrow_date = today_date + datetime.timedelta(days=1)
        start_of_tomorrow = (datetime.datetime(year = tomorrow_date.year, month = tomorrow_date.month, day = tomorrow_date.day, hour = 0, minute = 1)).isoformat()+ 'Z'
        esiee_calendar_id = 'fd5c6ef22a216acd764d766347a1bcf0019ceadb8152137ae0a4744bb7707228@group.calendar.google.com'
        events_result = service.events().list(calendarId=esiee_calendar_id, timeMin=start_of_tomorrow,
                                              maxResults=max, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        # do stuff here
        tomorrow_events = []
        for event in events:
            event_day = (datetime.datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')).day
            tomorrow = tomorrow_date.day

            if (event_day == tomorrow):
                tomorrow_events.append(event)

        return tomorrow_events
        
    except HttpError as error:
        print('An error occurred: %s' % error)
        return ([])