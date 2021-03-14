import datetime

import discord
from discord.ext import commands

from utils.functions import read_json, get_prefix

'''
Discord.py is an API wrapper for Discord written in python

Common recurring themes:
 - a 'Guild':
    a Guild is what discord uses to refer to a server. Events detected by the bot can either be within a guild channel 
    or a Direct Message Channel. 
 - ctx or 'context':
    The context is an argument passed when a command is invoked, it wraps the context which a command is invoked under
    attributes include:
     - author (returns a Member object of the command invoker)
     - bot (returns the object of commands.Bot that encompasses the entire system)
     - channel (returns a channel object in which the command was invoked)
     - message (the message object of the message in which the command was invoked)
     - prefix (the prefix used to invoke the command)
     - kwargs (the arguments passed into the command in dictionary form)
     - guild (the server or 'guild' the command was invoked in)
 - discord.Embed():
    An embedded message that can only be used by bot user accounts. It is quite powerful and can format messages in an 
    aesthetically pleasing form.
 - Cogs:
    a Cog as defined by discord is: "a collection of commands, listeners, and optional state to help group commands 
    together"
    They are used in this project to categorize and group commands to increase efficiency
 - Extensions:
    An extension is a python module, in this project each extension contains a single cog class and a global "setup" 
    function for discord.py to run.
'''

# stores the current config json in a dictionary to be accessed
config = read_json('config')

token = config['BOT_TOKEN']  # retrieves the bot token from the config
DEFAULT_PREFIX = config['DEFAULT_PREFIX']

# Initializes the intents the bot has; this is basically informing discord of what data the bot would like to collect
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents)

bot.owners = config['BOT_OWNERS']

bot.colours = {
    'RED': 0xFF0000,
    'GREEN': 0x00FF00,
    'BLUE': 0x0000FF,
    'BOT_COLOUR': 0x4C37C9
}  # adds a dictionary to the global "bot" object that will allow for easy access of different colours,
# including the default bot colour.

# all the extensions are defined and the bot attempts to load each extension; if an error is raised it will simply
# catch the error and print it out
extensions = [
    'cogs.commands.music',
    'cogs.commands.configuration',
    'cogs.events',
    'cogs.commands.developer_tools'
]

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
            print(
                f"[{datetime.datetime.utcnow().replace(microsecond=0)} INFO]: [Extensions] {extension} loaded successfully")
        except Exception as e:
            print(
                f"[{datetime.datetime.utcnow().replace(microsecond=0)} INFO]: [Extensions] {extension} didn't load {e}")

bot.run(token)
