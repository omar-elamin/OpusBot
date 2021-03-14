import discord
from discord.ext import commands

from utils.functions import read_json, write_json


# the Cog that groups commands that involve configuration of the bot
class Config(commands.Cog):
    def __init__(self, bot):
        """ A set of commands used to edit settings that directly affect the bot's behaviour. """
        self.bot = bot

    @commands.command(aliases=['changeprefix', 'setprefix'])
    @commands.has_permissions(manage_guild=True)
    # Sets a new prefix for the bot within a given guild
    async def prefix(self, ctx, prefix):
        prefixes = read_json('prefixes')
        prefixes[str(ctx.guild.id)] = prefix  # stores the new prefix into the dictionary and writes it to the json file
        write_json('prefixes', prefixes)

        em = discord.Embed()
        em.title = 'Prefix changed'
        em.description = f'`{ctx.prefix}` -> `{prefix}`'  # Displays the information
        em.colour = self.bot.colours['BOT_COLOUR']

        await ctx.send(embed=em)

    @commands.command(aliases=['djrole', 'changedj', 'dj'])
    @commands.has_permissions(manage_guild=True)
    # Defines or sets a new DJ role within a given guild
    async def setdj(self, ctx, djrole: discord.Role):
        djroles = read_json('djroles')
        djroles[str(
            ctx.guild.id)] = djrole.id  # writes the ID of the given role to the json file with the key being
        # the ID of the server
        write_json('djroles', djroles)

        em = discord.Embed()
        em.title = 'DJ Role updated'  # Sets the Embed title
        em.description = f'-> `{djrole.name}`'  # sets the embed description field
        em.colour = self.bot.colours['BOT_COLOUR']  # sets the embed colour

        await ctx.send(embed=em)  # Displays the information


# Global setup function for discord.py
def setup(bot):
    bot.add_cog(Config(bot))
