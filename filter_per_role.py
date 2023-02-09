import discord
from discord import app_commands
from discord.ext import commands

english_roles = {
    "Ia": 0,
    "Ib": 1,
    "Ic": 2,
    "Id": 3,
    "Ie": 4,
    "If": 5,
    "Ig": 6,
    "Ih": 7,
    "Ii": 8,
    "Ij": 9,
}


def get_command_user_roles(interaction):
    try:
        result = interaction.user.roles
    except:
        result = []
    return result


def get_english_role(roles):
    for role in roles:
        if role.name in english_roles:
            english_role = english_roles[role.name]
            return english_role
    return -1


def get_english_group_specific_info(event_info, english_group=-1):
    if english_group == -1:
        return event_info
    else:
        lines = event_info.splitlines()
        if "----" in event_info:
            # cours en présentiel
            line1 = lines[3*english_group]
            line2 = lines[3*english_group+1]
            info_value = [line1, line2]
            return "\n".join(info_value)
        else:
            #cours en distanciel
            return lines[english_group]


