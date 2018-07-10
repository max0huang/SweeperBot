README file for SweeperBot
==========================

**Currently under heavy development. More features coming!**

**Contents:**
1. [Introduction](#introduction)
1. [Features](#features)
1. [Dependencies](#dependencies)
1. [Setup](#setup)

# Introduction

This is SweeperBot, a (slightly RPG themed) Discord bot that automatically removes old messages.

# Features

- `!say_hi` - Introduces bot to guild. 
- `!clean_channel` - Cleans the channel the command was run in.

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
