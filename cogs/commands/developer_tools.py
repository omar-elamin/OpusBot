import asyncio

import discord
from discord.ext import commands

import utils.checks as checks


class DevTools(commands.Cog, name='Developer Tools'):
    def __init__(self, bot):
        """A set of tools for the bot developer to use when testing the bot."""
        self.bot = bot

    @checks.is_developer()  # Checks that the person sending the command is a bot developer.
    @commands.command(aliases=['eval'])
    async def debug(self, ctx, code):
        """Executes a line of code for debugging."""
        em = discord.Embed()
        em.title = 'Result'
        em.colour = self.bot.colours['BOT_COLOUR']
        try:
            result = eval(code)  # evaluates a line of code
            if asyncio.iscoroutine(result):  # if the function is asynchronous, it will await it
                result = await result
            em.description = str(result)
        except Exception as e:
            em.description = f'{type(e).__name__}: {e}'  # send feedback to user

        await ctx.send(embed=em)

    @checks.is_developer()  # Checks that the person sending the command is a bot developer.
    @commands.command()
    async def shutdown(self, ctx):
        """ Shuts down the bot. """
        em = discord.Embed()
        em.title = 'Shutdown'
        em.description = 'Bot offline.'
        em.colour = self.bot.colours['BOT_COLOUR']

        await ctx.send(embed=em)
        await self.bot.logout()  # Shuts down the bot.


def setup(bot):
    bot.add_cog(DevTools(bot))
