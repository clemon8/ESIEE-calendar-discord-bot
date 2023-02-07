import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import json

bot = commands.Bot(command_prefix='/', intents = discord.Intents.all())

def get_bot_token():
    """Gets the discord bot token

    This function returns the discord bot token stored in the `config.json` file
    """
    with open('config.json') as f:
        config_data = json.load(f)
        token = config_data['token']
    return token

# Bot Event
@bot.event
async def on_ready():
    """Executed function when the bot is ready

    This function syncs the bot commands and print if he initialised well
    """

    print("Ready to analyse some Spotify data!")
    try:
        # Sync the bot commands
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")

    except Exception as e:
        print(e)


# Classic Artist Stats Command
@bot.tree.command(name="artist_stats", description="Retrieves the stats from an artist")
@app_commands.describe(artist = "Artist name or Spotify share link")

async def artist_stats(interaction: discord.Interaction, artist: str):
    # Defer to not get kicked out
    await interaction.response.defer(thinking=True)

    try:

            # Define the embed
            answer_embed = discord.Embed(color=0x1ed760, title=artist, type='rich')
            answer_embed.add_field(name=":fire: Popularity Score", value="⚠️ wip", inline=False)
            
            answer_embed.set_footer(text="ESIEE Calendar powered by Google Calendar API", icon_url='https://raw.githubusercontent.com/clemon8/statisfy-discord-bot/main/src/statisfy_icon.png')

            answer_embed.color = discord.Colour.brand_red


            # Adding a button
            view = View()
            """ button_artist_profile = Button(label='Artist Profile', style=discord.ButtonStyle.url, url=link)
            button_artists_suggestions = Button(label="Related Artists", style=discord.ButtonStyle.secondary)

            # Artist Suggestions Button
            async def related_artists_button(interaction):
                related_artists_title = f"{artist} Related Artists:"
                related_artists_embed = discord.Embed(color= answer_embed.color, title=related_artists_title, type = "rich")
                if len(related_artists) == 0:
                    related_artists_embed.add_field(name = "",inline=False, value = "No related Artists yet")
                else:
                    for related_artist in related_artists:
                        related_artist_name = related_artist['name']
                        related_artist_url = related_artist['url']
                        related_artist_followers = '{:,}'.format(related_artist["followers"]).replace(',', ' ')
                        field_value = f"[{related_artist_name}]({related_artist_url}) ({related_artist_followers} followers)\n"
                        related_artists_embed.add_field(name="", inline=False, value = field_value)
                await interaction.response.send_message(embed= related_artists_embed)
            
            button_artists_suggestions.callback = related_artists_button

            view.add_item(button_artists_suggestions)
            view.add_item(button_artist_profile) """
            

            # Sending the message
            await interaction.followup.send(embed=answer_embed, view=view)


    # Error occured in the slash command
    except Exception as e:
        print(e)
        await interaction.followup.send(f"couldn't retrieve the calendar sorry :/", ephemeral=True)


# Run the bot
bot.run(get_bot_token())