import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import json

import datetime
import os.path
import unicodedata
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

bot = commands.Bot(command_prefix='/', intents = discord.Intents.all())


# Google Calendar Part

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = "fd5c6ef22a216acd764d766347a1bcf0019ceadb8152137ae0a4744bb7707228@group.calendar.google.com"

def get_bot_token():
    """Gets the discord bot token

    This function returns the discord bot token stored in the `config.json` file
    """
    with open('config.json') as f:
        config_data = json.load(f)
        token = config_data['discord_token']
    return token

def clean_calendar_description(description):
    lines = description.splitlines()
    if lines and lines[-1].startswith("ADE: (Exported"):
        description = "\n".join(lines[:-1])
    return description
    


def get_today_events():

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
                                              maxResults=5, singleEvents=True,
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

# Bot Event
@bot.event
async def on_ready():
    """Executed function when the bot is ready

    This function syncs the bot commands and print if he initialised well
    """

    print("Ready to give some dates 0_o")
    try:
        # Sync the bot commands
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")

    except Exception as e:
        print(e)


# Cours du jour
@bot.tree.command(name="aujourdhui", description="Qu'est ce qu'on a au menu aujourd'hui?")
@app_commands.describe()

async def artist_stats(interaction: discord.Interaction):
    # Defer to not get kicked out
    await interaction.response.defer(thinking=True)

    try:
        # Define the embed
        answer_embed = discord.Embed(color=0xd55044, title="Aujourd'hui", type='rich')

        events = get_today_events()

        resume = "Pas de cours aujourd'hui 💤"
        if len(events) != 0:
            resume = f"{len(events)} cours aujourd'hui 📚"
        answer_embed.add_field(name="", value=resume, inline=False)

        for event in events:
            start = event['start']['dateTime']
            start_hour = (datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')).strftime('%H:%M')
            end = event['end']['dateTime']
            end_hour = (datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z')).strftime('%H:%M')
            name = event['summary']

            if 'location' in event: classe = event['location']
            else: classe = ''

            if 'description' in event: info = clean_calendar_description(event['description'])
            else: info = ''

            value = info + '\n' + classe

            answer_embed.add_field(name=f"{start_hour} - {end_hour}: {name}", value=f"{value}", inline=False)


        answer_embed.set_footer(text="ESIEE Calendar powered by Google Calendar API", icon_url='https://raw.githubusercontent.com/clemon8/ESIEE-calendar-discord-bot/main/src/esiee_calendar_icon.png')


        # Adding a button
        view = View()

        # Sending the message
        await interaction.followup.send(embed=answer_embed, view=view)


    # Error occured in the slash command
    except Exception as e:
        print(e)
        await interaction.followup.send(f"couldn't retrieve the calendar sorry :/", ephemeral=True)


# Run the bot
bot.run(get_bot_token())