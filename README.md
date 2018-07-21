README file for SweeperBot
==========================

**Currently under heavy development. More features coming!**

**Contents:**
1. [Introduction](#introduction)
2. [Features](#features)
3. [Dependencies](#dependencies)
4. [Setup](#setup)

# Introduction

This is SweeperBot, a (slightly RPG themed) Discord bot that automatically removes old messages.

# Features

- `!s help`
	- Displays a list of the commands and their descriptions.
- `!s say_hi`
	- Does a self introduction.
- `!s clean_channel`
	- Cleans the channel the command was run in.
- `!s auto_clean channels #channel_name for_messages older_than x time`
	- Automatically removes messages that are older than x time from #channel_name.
	- e.g. `!s auto_clean channels #channel_one #channel_two for_messages older_than 1 hour 30 minutes`
	- This command accepts one or more channels.
	- Valid time parameters are second(s), minute(s), hour(s), day(s), week(s), month(s) and year(s).
	- Decimals, specifically any _real number_, may be used.
	- The interval of time is resolved to the closest second and is artificially capped to one year.
-  `!s auto_clean_remove channels #channel_name for_messages older_than x time`
	- Removes specified scheduled auto_clean tasks.
	- e.g. `!s auto_clean_remove channels #channel_one #channel_two for_messages older_than 1 hour 30 minutes`
	- This command accepts anything that the command auto_clean accepts.
	- It doesn't matter how you describe the interval of time - as long as the specified interval for older_than matches the auto_clean task you want to remove, it will be removed.
		- i.e. older_than 1 hour = older_than 60 minutes as the interval of time is the same.

# Dependencies

- python >= 3.6
- pip
- virtualenv (optional)

# Setup

1. Apply for the bot at https://discordapp.com/developers/applications/me . The bot needs the permissions to read, write and manage messages on the channels which you want to use it on.
2. Clone this repository. `git clone https://github.com/maxhuang/SweeperBot.git`
3. Change directory into the cloned repository. `cd SweeperBot`
4. Create a file called `authentication_token.txt` and place the bot's authentication token within that file. `echo "BOT_AUTHENTICATION_TOKEN" > ./authentication_token.txt`
5. Setup and enter a python virtualenv (optional)
6. Install the rewrite version of discordpy from git using pip. `pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]`
7. Run the bot. `python SweeperBot.py`
