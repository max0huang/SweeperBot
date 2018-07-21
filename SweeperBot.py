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

def convenient_check(*args):
    """ Print type and str representation of object. """
    for arg in args:
        print(type(arg), '\n\t', arg, '\n', sep='')

def is_valid_float(test_string):
    try:
        float(test_string)
    except:
        return False
    return True

def parse_arguments(ctx, argument_type):
    """ Parse arguments and return them in a dictionary """
    command_tokens = ctx.message.content[len(ctx.prefix):].split()[1:]
    command_arguments = {}

    # Extract layout
    previous_parameter = None
    for token in command_tokens:
        # All parameters have arguments not just solo
        if token.lower() in ['channels', 'for_messages', 'older_than']:
            previous_parameter = token.lower()
        elif previous_parameter != None:
            if previous_parameter in command_arguments:
                command_arguments[previous_parameter] += str(
                        token.lower() + ' ' )
            else:
                command_arguments[previous_parameter] = str(
                        token.lower() + ' ')
        else:
            raise commands.BadArgument()

    # Extract channels
    matches = re.findall(r'<#([0-9]+)>', command_arguments['channels'])
    command_arguments['channels'] = []

    if not matches:
        raise commands.MissingRequiredArgument()

    for match in matches:
        # Get channel object
        channel = sweeper_bot.get_channel(int(match))
        if channel:
            command_arguments['channels'] += [channel]
        else:
            raise commands.BadArgument()

    # Extract interval
    interval = 0

    matches = re.findall(
            r"(([0-9]+\s(year|month|day|hour|minute|second)s?))+",
            command_arguments['older_than'])

    if not matches:
        raise commands.MissingRequiredArgument
    
    for match in matches:
        quantity, unit = match[0].split()
        
        if is_valid_float(quantity):
            quantity = abs(float(quantity))
        else:
            raise commands.BadArgument()
    
        if unit in ['second', 'seconds']:
            interval += quantity
        elif unit in ['minute', 'minutes']:
            interval += 60 * quantity
        elif unit in ['hour', 'hours']:
            interval += 60 * 60 * quantity
        elif unit in ['day', 'days']:
            interval += 24 * 60 * 60 * quantity
        elif unit in ['week', 'weeks']:
            interval += 7 * 24 * 60 * 60 * quantity
        elif unit in ['month', 'months']:
            interval += 30 * 24 * 60 * 60 * quantity
        elif unit in ['year', 'years']:
            interval += 365 * 24 * 60 * 60 * quantity
        else:
            raise commands.BadArgument()
    
        # Limit interval to a year inclusive
        interval = round(interval)
        if interval <= 365 * 24 * 60 * 60:
            command_arguments['older_than'] = interval
        else:
            raise commands.BadArgument()

    return command_arguments

async def long_sleep(interval):
    """ Basically asyncio.sleep() without time limits """
    #_max_timeout = 2147483.5
    max_timeout = 3600 * 24

    interval_remaining = interval
    while interval_remaining >= 0:
        if interval_remaining >= max_timeout:
            timeout = max_timeout
            interval_remaining -= max_timeout
        else:
            timeout = interval_remaining
            interval_remaining -= max_timeout
        await asyncio.sleep(timeout)

async def load_scheduled_tasks():
    """ Loads deletion schedules from sqlite database. """
    pass

async def save_scheduled_task():
    """ Insert task into sqlite database. """
    pass

async def remove_scheduled_task():
    """ Remove task from sqlite database. """
    pass

async def add_task_to_queue(future, task_arguments):
    """ Adds deletion task to bot's queue. """
    interval = datetime.timedelta(seconds=task_arguments[2])

    # Need to implement sleep till next closest message
    await long_sleep(2)

    await clear_history(task_arguments[1], -interval)

    future.set_result(task_arguments)

def requeue_task(returned_future):
    """ Callback function that requeues add_task_to_queue """
    task_arguments = returned_future.result()

    future = asyncio.Future()
    future.add_done_callback(requeue_task)
    task = asyncio.ensure_future(
            add_task_to_queue(future, task_arguments))
    sweeper_bot.scheduled_tasks[task_arguments] = task
    
def remove_task_from_queue(task_arguments):
    """ Remove deletion task from bot's queue. """
    task = sweeper_bot.scheduled_tasks[task_arguments]
    task.cancel()

    del sweeper_bot.scheduled_tasks[task_arguments]
    print(f"Sucessfully removed deletion task {task_arguments} from queue")

def check_user_permissions(channel, user, **permissions):
    """ Check if the user has the permissions for the channel """
    # Check user permissions
    channel_permissions = channel.permissions_for(user)
    missing_permissions = [p for p, v in permissions.items()
            if getattr(channel_permissions, p, None) != v]
    if missing_permissions:
        raise commands.MissingPermissions(missing_permissions)

    return True

def check_bot_permissions(channel, bot, **permissions):
    """ Check if the bot has the permissions for the channel """
    # Check bot permissions
    channel_permissions = channel.permissions_for(bot)
    missing_permissions = [p for p, v in permissions.items()
            if getattr(channel_permissions, p, None) != v]
    if missing_permissions:
        raise commands.BotMissingPermissions(missing_permissions)

    return True

async def clear_history(channel, clear_before_date_delta=None):
    """ Naive clearing of channel messages after a date given by 
    combining a date delta with utcnow. 
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
                        before=clear_before_date,
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
        read_messages=True,
        read_message_history=True,
        send_messages=True,
        manage_messages=True)
@commands.bot_has_permissions(
        read_messages=True,
        read_message_history=True,
        send_messages=True,
        manage_messages=True)
async def clean_channel(ctx):
    """ Cleans the channel the command was run in. """
    await clear_history(ctx.channel)

@sweeper_bot.command()
async def auto_clean(ctx):
    """ Schedule automatic cleaning of messages.
    Usage: auto_clean channels #channel_name for_messages older_than 
    time
    """
    command_arguments = parse_arguments(ctx, 'schedule')
    print(ctx.message.content, command_arguments, ctx.guild, None, sep='\n')

    for channel in command_arguments['channels']:
        task_arguments = (ctx.guild, channel, command_arguments['older_than'])

        # Check if bot and user have sufficent permissions
        check_user_permissions(
                channel,
                ctx.author,
                read_messages=True,
                read_message_history=True,
                send_messages=True,
                manage_messages=True)
        check_bot_permissions(
                channel,
                ctx.guild.get_member(sweeper_bot.user.id),
                read_messages=True,
                read_message_history=True,
                send_messages=True,
                manage_messages=True)

        future = asyncio.Future()
        future.add_done_callback(requeue_task)
        task = asyncio.ensure_future(
                add_task_to_queue(future, task_arguments))
        sweeper_bot.scheduled_tasks[task_arguments] = task

@sweeper_bot.command()
async def auto_clean_remove(ctx):
    """ Removes scheduled auto_clean tasks.
    Usage: auto_clean_remove channels #channel_name for_messages
    older_than time
    """
    command_arguments = parse_arguments(ctx, 'remove')
    print(ctx.message.content, command_arguments, ctx.guild, None, sep='\n')

    for channel in command_arguments['channels']:
        task_arguments = (ctx.guild, channel, command_arguments['older_than'])

        # Check if bot and user have sufficent permissions
        check_user_permissions(
                channel,
                ctx.author,
                read_messages=True,
                read_message_history=True,
                send_messages=True,
                manage_messages=True)
        check_bot_permissions(
                channel,
                ctx.guild.get_member(sweeper_bot.user.id),
                read_messages=True,
                read_message_history=True,
                send_messages=True,
                manage_messages=True)

        remove_task_from_queue(task_arguments)

@sweeper_bot.command()
async def auto_clean_list(ctx):
    """ Lists scheduled auto_clean tasks.
    Usage: auto_clean_list
    """
    pass

@sweeper_bot.event
async def on_ready():
    print("Successfuly connected to Discord as {}".format(sweeper_bot.user))

    # Confirm that 'scheduled_tasks' is empty so no overwriting occurs
    if not 'scheduled_tasks' in sweeper_bot.__dict__:
        sweeper_bot.scheduled_tasks = {}
    else:
        print("Error: 'scheduled_tasks' already exists. Please " \
                "file a bug report.")
        exit(1)

    await load_scheduled_tasks()

    for guild in sweeper_bot.guilds:
        for channel in guild.channels:
            channel_permissions = channel.permissions_for(
                    guild.get_member(sweeper_bot.user.id))
            if (str(channel.category).lower() == 'text channels'
                    and channel_permissions.read_messages
                    and channel_permissions.read_message_history
                    and channel_permissions.send_messages
                    and channel_permissions.manage_messages):
                print(type(channel), channel,
                        type(channel.category), channel.category)
                #print('about to clear history')
                #await clear_history(channel, -datetime.timedelta(seconds=10))

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

print('Link Start!')

# A blocking call that abstracts away the event loop initialisation from you.
sweeper_bot.run(authentication_token)
