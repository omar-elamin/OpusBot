import discord
from discord.ext import commands

from music_master import players
from utils import functions, checks


class Music(commands.Cog):  # Initializes Music cog. Creates a category of commands called Music
    def __init__(self, bot):
        """A set of commands used to control the music."""
        self.bot = bot
        self.bot.PlayerManager = players.PlayerManager()  # Initializes the bot's player manager

    @commands.command()
    async def join(self, ctx):
        """Joins a Voice Channel."""
        em = discord.Embed()
        em.title = 'Music'
        em.color = self.bot.colours['BOT_COLOUR']

        guild_id = ctx.guild.id

        member = ctx.author
        vc = member.voice.channel
        if member and member.voice:  # checks if the member of the server who invoked the command is connected to a
            # voice channel
            player = self.bot.PlayerManager.new_player(guild_id)  # Creates a new player object for the current server
            if not player.is_connected:  # checks if the player is not currently connected to a voice channel
                await player.connect_to(ctx.guild.id, member.voice.channel.id,
                                        self.bot)  # if it isn't it will connect to the user's channel
                em.description = f'Joined {vc.name}'
        else:
            em.description = 'No voice channel found.'
        await ctx.send(embed=em)  # Sends an embedded message to the channel in which the command was invoked,
        # with user feedback

    # calls a check before running the command to check if the user sending the command is alone in the voice
    # channel, or if they have the appropriate permissions (DJ role, manage server permissions, etc)
    @checks.is_alone_or_dj()
    @commands.command(aliases=['dc', 'disconnect', 'stop'])
    async def leave(self, ctx):
        """Leaves the Voice Channel."""
        em = discord.Embed()
        em.title = 'Music'
        em.colour = self.bot.colours['BOT_COLOUR']
        player = self.bot.PlayerManager.get_player(ctx.guild.id)  # retrieves the current server's player object

        if not player.is_connected:  # if the player isn't connected, the bot will inform the user accordingly
            em.description = 'Not currently connected to a channel.'
            em.colour = self.bot.colours['RED']

        # Checks if the user sending the command is not in the same voice channel as the bot.
        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            em.description = 'You must be in the same Voice Channel as the bot to disconnect it.'
        else:  # Otherwise it will clear the queue and leave the voice channel and stop the Player.
            player.queue.clear_queue()
            await player.connect_to(ctx.guild.id, None, self.bot)
            await player.stop()

            em.description = 'Disconnected.'

        await ctx.send(embed=em)

    @commands.command(aliases=['p'])
    async def play(self, ctx, query):
        em = discord.Embed()
        em.title = 'Music'
        em.colour = self.bot.colours['BOT_COLOUR']

        player = self.bot.PlayerManager.get_player(ctx.guild.id)  # retrieves the player from the player manager
        #  connects to the user's voice channel if the player is not currently connected
        if not player.is_connected and ctx.author.voice.channel:
            player.connect_to(ctx.guild.id, ctx.author.voice.channel.id, self.bot)
        if player.is_connected:
            # returns a song object or a list of song objects from the query
            song = await functions.query_to_song(query, self.bot.PlayerManager.get_player(ctx.guild.id))
            if isinstance(song, list):  # checks if query returned a playlist or a singular song and queues accordingly
                for song_object in song:
                    player.add_song(song_object)
                em.description = f'Added {len(song)} songs to queue'
            else:
                print(player)
                player.add_song(song)  # adds Song
                em.description = f'Added {song.title} to queue'

        else:
            em.description = 'Bot is not connected to a voice channel'

        await ctx.send(embed=em)

        if not player.is_playing:
            await player.play()


def setup(bot):
    bot.add_cog(Music(bot))
