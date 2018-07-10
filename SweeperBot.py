import discord
from discord.ext import commands

import traceback
import asyncio
import datetime
import re

# Get authentication token from file assumed to be in same directory
authentication_token = open('authentication_token.txt').readline().strip()

# Instantiate client
sweeper_bot = commands.Bot(command_prefix = '!s ')

def convenient_check(object_to_check):
    """ Print type and str representation of object. """
    print(type(object_to_check), object_to_check)

async def load_scheduled_tasks():
    """ Loads deletion schedules from sqlite database. """
    pass

async def save_scheduled_task():
    """ Insert task into sqlite database. """
    pass

async def remove_scheduled_task():
    """ Remove task from sqlite database. """
    pass

async def add_task_to_queue():
    """ Adds deletion task to bot's queue. """
    pass

async def remove_task_from_queue():
    """ Removes deletion task from bot's queue. """
    pass

async def check_permissions(ctx):
    print("Didn't check permissions.")
    return True

async def get_channel_id_by_name(ctx, channel_name):
    """ Returns the id of a channel of the same name """
    pass

async def clear_history(channel, clear_before_date_delta=None):
    """ Naive clearing of channel messages after a date given by combining a
    date delta with utcnow. 
    """
    try:
        if clear_before_date_delta == None:
            # Clean all
            while True:
                deleted = await channel.purge(
                        limit=1000,
                        reverse=True)
                if len(deleted) == 0:
                    break
        else:
            # Clean before date
            clear_before_date = datetime.datetime.utcnow() \
                    + clear_before_date_delta
            while True:
                deleted = await channel.purge(
                        limit=1000,
                        after=clear_before_date,
                        reverse=True)
                if len(deleted) == 0:
                    break
    except discord.Forbidden:
        print("Forbidden: Please give me permission to perform my job!")
        await channel.send("Please give me permission to perform my job!")
    except discord.HTTPException:
        print("HTTPException: Deleting the messages failed!?")
        await channel.send("Deleting the messages failed!?")

@sweeper_bot.command()
@commands.has_permissions(
        read_messages=True, send_messages=True)
@commands.bot_has_permissions(
        read_messages=True, send_messages=True)
async def say_hi(ctx):
    """ Introduces bot to guild. """
    await ctx.send("Hello guild, I'm {}. I look forwards to keeping the " \
            "rooms clean and tidy!".format(sweeper_bot.user))

@sweeper_bot.command()
@commands.has_permissions(
        read_messages=True, send_messages=True, manage_messages=True)
@commands.bot_has_permissions(
        read_messages=True, send_messages=True, manage_messages=True)
async def clean_channel(ctx):
    """ Cleans the channel the command was run in. """
    await clear_history(ctx.channel)

@sweeper_bot.command()
async def auto_clean(ctx):
    """ Cleans messages according to the conditions set by user(s).
    Usage: auto_clean channels #channel_name for_messages older_than time
    """
    print(ctx.message.content)
    #print(ctx.message, ctx.prefix, ctx.args, ctx.kwargs)
    #await clear_history(channel, datetime.timedelta(days=-1))

    command_tokens = ctx.message.content[len(ctx.prefix):].split()[1:]
    command_arguments = {}

    previous_parameter = None
    for token in command_tokens:
        # All parameters have arguments not just solo
        if token.lower() in ['channels', 'for_messages', 'older_than']:
            previous_parameter = token.lower()
        elif previous_parameter != None:
            if previous_parameter in command_arguments:
                command_arguments[previous_parameter] += [token.lower()]
            else:
                command_arguments[previous_parameter] = [token.lower()]
        else:
            raise commands.UserInputError()

    previous_token = None
    date_arguments = {}
    if 'older_than' in command_arguments:
        for token in command_arguments['older_than']:
            if previous_token:
                previous_token = token
                continue
            if previous_token in ['year', 'month', 'day', 'hour', 'minute',
                    'second']:
                # Add keypairs
                pass
            elif

    for channel in command_arguments['channels']:
        match = re.search(r'^<#([0-9]+)>', channel)
        if not match:
            raise commands.UserInputError()
        channel_id = sweeper_bot.get_channel(eval(match[1]))
        if not channel_id:
            raise commands.UserInputError()
        convenient_check(channel_id)

@sweeper_bot.event
async def on_ready():
    print("Successfuly connected to Discord as {}".format(sweeper_bot.user))

    await load_scheduled_tasks()

    for guild in sweeper_bot.guilds:
        for channel in guild.channels:
            channel_permissions = channel.permissions_for(
                    guild.get_member(sweeper_bot.user.id))
            if (str(channel.category).lower() == 'text channels'
                    and channel_permissions.read_messages
                    and channel_permissions.send_messages
                    and channel_permissions.manage_messages):
                print(type(channel), channel,
                        type(channel.category), channel.category)

@sweeper_bot.event
async def on_command_error(ctx, error):
    """ Error handling for errors raised during command invocation
    ctx     : Context
    error   : Exception
    """
    # Prevent commands with local handlers being handled here
    if hasattr(ctx.command, 'on_error'):
        return
    
    if isinstance(error, commands.CommandNotFound):
        print("CommandNotFound: Exception raised when a command is " \
                "attempted to be invoked but no command under that name is " \
                "found.")
        return await ctx.send("Sorry, I don't understand what you mean by " \
                "{}.".format(ctx.message.content))

    # Print default traceback for errors that have not returned
    print("Caught exception in command: {}".format(ctx.command))
    traceback.print_exception(type(error), error, error.__traceback__)
    # DEBUG:
    convenient_check(ctx)
    convenient_check(error)
    print("Caught exception in command: {}".format(ctx.message.content))

print('Link スタート!')

# A blocking call that abstracts away the event loop initialisation from you.
sweeper_bot.run(authentication_token)
