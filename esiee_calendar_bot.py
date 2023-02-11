import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View
import json

import datetime
import locale
import asyncio

import calendar_requests as cr
import customization as cz
import filter_per_role as fr

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

def get_last_daily_message_id():
    """Gets the last daily message id

    This function returns the the last daily message id stored in the `temp.json` file
    """
    with open('temp.json') as f:
        config_data = json.load(f)
        id = config_data['last_daily_message_id']
    return id

def update_last_daily_message_id(new_id: int):
    """Updates the last daily message id

    This function takes an integer parameter `new_id` and overwrites the last daily message id
    stored in the `temp.json` file with it
    """
    with open('temp.json', 'r') as f:
        config_data = json.load(f)

    config_data['last_daily_message_id'] = new_id

    with open('temp.json', 'w') as f:
        json.dump(config_data, f)

def clean_calendar_description(description):
    lines = description.splitlines()
    if lines and lines[-1].startswith("ADE: (Exported"):
        description = "\n".join(lines[:-1])
    return description


def format_events(events, interaction = None, custom_roles=False):
    result = []
    for event in events:
            start = event['start']['dateTime']
            start_hour = (datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')).strftime('%H:%M')
            end = event['end']['dateTime']
            end_hour = (datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z')).strftime('%H:%M')
            name = event['summary']
            emoji = cz.get_class_emoji(name)

            if 'location' in event: classe = event['location']
            else: classe = ''

            if 'description' in event: info = clean_calendar_description(event['description'])
            else: info = ''

            if custom_roles:
            # check if english class
                if len(info.splitlines()) > 6:
                    english_group = fr.get_english_role(fr.get_command_user_roles(interaction))
                    info = fr.get_english_group_specific_info(info, english_group)

            value = info + '\n' + classe

            current_event = {
                "name": f"{start_hour} - {end_hour}: {emoji} {name}",
                "value": value
            }

            result.append(current_event)
    return result

def get_ade_export_datetime(events):
    if len(events) == 0:
        return datetime.datetime.now()
    result = datetime.datetime.now() - datetime.timedelta(days=100)
    for event in events:
        if 'description' in event: 
            info = event['description']
            lines = info.splitlines()
            if lines and lines[-1].startswith("ADE: (Exported"):
                date_string = lines[-1][16:32]
                date_format = "%d/%m/%Y %H:%M"
                datetime_object = datetime.datetime.strptime(date_string, date_format)
                result = max(datetime_object, result)
    
    return result


async def daily_aujourdhui(channel_id = 1074060824425017475):

    channel = bot.get_channel(channel_id)

    # Change previous message
    previous_message_id = get_last_daily_message_id()
    if previous_message_id != 0:
        previous_message = await channel.fetch_message(previous_message_id)
        embed = previous_message.embeds[0]

        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')
        formatted_date = yesterday.strftime("%A %d %B %Y")
        embed.title = formatted_date
        await previous_message.edit(embed=embed)

    # Define the embed
    answer_embed = discord.Embed(color=0xd55044, title="Aujourd'hui", type='rich')

    events = cr.get_today_events()

    resume = "Pas de cours aujourd'hui 💤"
    if len(events) != 0:
        resume = f"{len(events)} cours aujourd'hui 📚"
    answer_embed.add_field(name="", value=resume, inline=False)

    formated_events = format_events(events, None, False)
    for formated_event in formated_events:
        answer_embed.add_field(name=formated_event['name'], value=formated_event['value'], inline=False)

    answer_embed.set_footer(text="Powered by Google Calendar API",
    icon_url='https://raw.githubusercontent.com/clemon8/ESIEE-calendar-discord-bot/main/src/esiee_calendar_icon.png')

    answer_embed.timestamp = get_ade_export_datetime(events)

    # Sending the message
    
    sent_message = await channel.send(embed=answer_embed)

    sent_message_id = sent_message.id
    update_last_daily_message_id(sent_message_id)


async def schedule_daily_message():
    while True:
        now = datetime.datetime.now()
        then = now+datetime.timedelta(minutes=1)
        then = then.replace(second=0, microsecond=0)
        wait_time = (then-now).total_seconds()
        print(f"next daily message at: {then}")
        await asyncio.sleep(wait_time)

        channel_id = 1074060824425017475
        await daily_aujourdhui(channel_id)

# Bot Event
@bot.event
async def on_ready():
    """Executed function when the bot is ready

    This function syncs the bot commands and print if he initialised well
    """

    await schedule_daily_message()

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

async def cours_aujourdhui(interaction: discord.Interaction):
    # Defer to not get kicked out
    await interaction.response.defer(thinking=True)

    try:
        # Define the embed
        answer_embed = discord.Embed(color=0xd55044, title="Aujourd'hui", type='rich')

        events = cr.get_today_events()

        resume = "Pas de cours aujourd'hui 💤"
        if len(events) != 0:
            resume = f"{len(events)} cours aujourd'hui 📚"
        answer_embed.add_field(name="", value=resume, inline=False)

        formated_events = format_events(events, interaction, True)
        for formated_event in formated_events:
            answer_embed.add_field(name=formated_event['name'], value=formated_event['value'], inline=False)

        answer_embed.set_footer(text="Powered by Google Calendar API",
        icon_url='https://raw.githubusercontent.com/clemon8/ESIEE-calendar-discord-bot/main/src/esiee_calendar_icon.png')

        answer_embed.timestamp = get_ade_export_datetime(events)

        # Adding a button
        view = View()

        # Sending the message
        await interaction.followup.send(embed=answer_embed, view=view)

    # Error occured in the slash command
    except Exception as e:
        print(e)
        await interaction.followup.send(f"couldn't retrieve the calendar sorry :/", ephemeral=True)


# Prochains Cours du jour
@bot.tree.command(name="prochains_aujourdhui", description="Qu'est ce qu'il nous reste aujourd'hui?")
@app_commands.describe()

async def prochains_cours_aujourdhui(interaction: discord.Interaction):
    # Defer to not get kicked out
    await interaction.response.defer(thinking=True)

    try:
        # Define the embed
        answer_embed = discord.Embed(color=0xd55044, title="Prochains Cours Aujourd'hui", type='rich')

        events = cr.get_next_events(istoday= True)

        resume = "Plus de cours aujourd'hui, au dodo! 💤"
        if len(events) != 0:
            resume = f"Encore {len(events)} cours aujourd'hui 📚"
        answer_embed.add_field(name="", value=resume, inline=False)

        formated_events = format_events(events, interaction, True)
        for formated_event in formated_events:
            answer_embed.add_field(name=formated_event['name'], value=formated_event['value'], inline=False)

        answer_embed.set_footer(text="ESIEE Calendar powered by Google Calendar API",
        icon_url='https://raw.githubusercontent.com/clemon8/ESIEE-calendar-discord-bot/main/src/esiee_calendar_icon.png')

        answer_embed.timestamp = get_ade_export_datetime(events)

        # Adding a button
        view = View()

        # Sending the message
        await interaction.followup.send(embed=answer_embed, view=view)

    # Error occured in the slash command
    except Exception as e:
        print(e)
        await interaction.followup.send(f"couldn't retrieve the calendar sorry :/", ephemeral=True)



# Prochain Cours
@bot.tree.command(name="prochain_cours", description="Quel est le prochain cours?")
@app_commands.describe()

async def prochain_cours(interaction: discord.Interaction):
    # Defer to not get kicked out
    await interaction.response.defer(thinking=True)

    try:
        # Define the embed
        answer_embed = discord.Embed(color=0xd55044, title="Prochain Cours", type='rich')

        events = cr.get_next_events(max=1)

        if len(events) == 0:
            resume = "Pas de prochain cours en vue! A toi le chômage! 🔥"
            answer_embed.add_field(name="", value=resume, inline=False)

        formated_events = format_events(events, interaction, True)
        for formated_event in formated_events:
            answer_embed.add_field(name=formated_event['name'], value=formated_event['value'], inline=False)

        answer_embed.set_footer(text="ESIEE Calendar powered by Google Calendar API",
        icon_url='https://raw.githubusercontent.com/clemon8/ESIEE-calendar-discord-bot/main/src/esiee_calendar_icon.png')

        answer_embed.timestamp = get_ade_export_datetime(events)

        # Adding a button
        view = View()

        # Sending the message
        await interaction.followup.send(embed=answer_embed, view=view)

    # Error occured in the slash command
    except Exception as e:
        print(e)
        await interaction.followup.send(f"couldn't retrieve the calendar sorry :/", ephemeral=True)


# Cours Demain
@bot.tree.command(name="cours_demain", description="Quel est le programme de demain?")
@app_commands.describe()

async def cours_demain(interaction: discord.Interaction):
    # Defer to not get kicked out
    await interaction.response.defer(thinking=True)

    try:
        # Define the embed
        answer_embed = discord.Embed(color=0xd55044, title="Cours Demain", type='rich')

        events = cr.get_tomorrow_events()

        resume = "Pas de cours demain, profite c'est pas tous les jours que ça arrive! 🍀"
        if len(events) != 0:
            resume = f"Au programme: {len(events)} cours demain 🤓"
        answer_embed.add_field(name="", value=resume, inline=False)

        formated_events = format_events(events, interaction, True)
        for formated_event in formated_events:
            answer_embed.add_field(name=formated_event['name'], value=formated_event['value'], inline=False)

        answer_embed.set_footer(text="ESIEE Calendar powered by Google Calendar API",
        icon_url='https://raw.githubusercontent.com/clemon8/ESIEE-calendar-discord-bot/main/src/esiee_calendar_icon.png')

        answer_embed.timestamp = get_ade_export_datetime(events)

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