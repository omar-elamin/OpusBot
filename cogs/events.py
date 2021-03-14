import discord
from discord.ext import commands

from utils import functions


# Creates the Events cog that will house all the listeners
class Events(commands.Cog):
    def __init__(self, bot):
        """A cog for all events invoked by discord."""
        self.bot = bot

    @commands.Cog.listener()  # calls the event listener native to commands.Cog
    async def on_guild_join(self, guild):  # every time the bot is added to a server; execute this code
        prefixes = functions.read_json('prefixes')
        config = functions.read_json('config')
        prefixes[str(guild.id)] = config[
            'DEFAULT_PREFIX']  # Add the current server id to the prefixes json file; and provide a default prefix
        functions.write_json('prefixes', prefixes)  # write data to json file

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):  # every time the bot is removed from/leaves a server; execute this code
        prefixes = functions.read_json('prefixes')
        prefixes.pop(str(guild.id))  # remove the server from the prefixes json file.
        functions.write_json('prefixes', prefixes)  # write data to json

        djroles = functions.read_json('djroles')
        if djroles[str(guild.id)]:  # if the server has a defined DJ role, remove it from the file
            djroles.pop(str(guild.id))
            functions.write_json('djroles', djroles)

    # If an error is detected while
    # attempting to run a command, run this code instead
    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    # pass
    # print(f'Error while running command: {error}')

    @commands.Cog.listener()
    async def on_message(self, message):  # Called whenever a message is sent.
        channel = message.channel
        # checks if the bot has been mentioned
        if f'<@{self.bot.user.id}>' in message.content or f'<@!{self.bot.user.id}>' in message.content:
            prefix = functions.get_prefix(self.bot, message)

            # Returns an embedded message giving information about the bot
            em = discord.Embed()
            em.title = 'Opus'
            em.description = f'`Prefix: {prefix}` (run {prefix}help for help)'  # provides the prefix of the bot in
            # the given guild
            em.colour = self.bot.colours['BOT_COLOUR']

            if len(self.bot.owners) == 1:  # if there is one bot owner defined, return their information
                em.add_field(
                    name='Owner',
                    value=f'`{self.bot.get_user(self.bot.owners[0])}`'
                )
            else:  # if there is more than one bot owner defined, return their usernames delimited by ','
                # and surrounded by '`' (markup formatting)
                em.add_field(
                    name='Owners',
                    value=f'`{"`, `".join([self.bot.get_user(self.bot.owners[i]) for i in self.bot.owners])}`'
                )

            await channel.send(embed=em)


def setup(bot):
    bot.add_cog(Events(bot))


class LavalinkEvent:
    """
    
    Base event.
    
    """


class EndOfQueue(LavalinkEvent):
    """
    
    Called when a queue reaches it's end and there are no more songs.
    
    """

    def __init__(self, player):
        self.player = player


class TrackStarted(LavalinkEvent):
    """
    
    Called when a track starts playing.
    
    """

    def __init__(self, player, track):
        self.player = player
        self.track = track


class TrackEnded(LavalinkEvent):
    """
    
    Called when a track stops playing.
    
    """

    def __init__(self, player, track, reason):
        self.player = player
        self.track = track
        self.reason = reason


class NodeConnected(LavalinkEvent):
    """
    
    Called when a Node is connected.
    
    """

    def __init__(self, node):
        self.node = node


class ClosedWebSocket(LavalinkEvent):
    """
    
    Called when the Web Socket is closed.
    
    """

    def __init__(self, player, code, reason):
        self.player = player
        self.code = code
        self.reason = reason
