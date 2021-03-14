from discord.ext import commands

from utils.functions import read_json, has_dj_role


def is_user_dj(ctx):  # a check to check if the user given has a role named dj or the defined DJ role.
    djroles = read_json('djroles')
    has_defined_role = djroles[str(ctx.guild.id)] in [role.id for role in ctx.author.roles]
    has_role_named_dj = "dj" in [role.name.lower() for role in ctx.author.roles]

    return has_defined_role or has_role_named_dj


def has_perms(ctx, **perms):  # checks if the user has a set of permissions, eg permission: "manage_roles=True"
    return all(getattr(ctx.channel.permissions_for(ctx.author), name, None) == value for name, value in
               perms.items())


def is_alone_or_dj():  # a global check to be called as a decorator before commands involving DJ level permissions
    def predicate(ctx):
        if has_dj_role(ctx.guild):
            if (len(ctx.author.voice.channel) == 1) or is_user_dj(ctx) or has_perms(ctx, manage_server=True):
                return True
            return False
        return True

    return commands.check(predicate)


def is_developer():  # a global check to be called as a decorator before commands involving Developer level permissions
    def predicate(ctx):
        return ctx.author.id in ctx.bot.owners
    return commands.check(predicate)
