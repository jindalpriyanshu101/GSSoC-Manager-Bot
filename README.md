# GSSoC Verification Bot

A Discord bot built for the GirlScript Summer of Code (GSSoC) and Winter of Blockchain (WoB) communities to manage user verification, role assignment, and other administrative tasks.

## Features

- 🔐 **User Verification**: Verifies users by email and assigns appropriate roles
- 👤 **Role Management**: Automatically assigns roles based on user participation type
- 📝 **Username Formatting**: Updates usernames to follow community standards
- 🔨 **Moderation Tools**: Includes commands for channel management and message cleanup
- 🤖 **Admin Commands**: Special commands for administrators to manage users

## Project Structure

The bot is organized into modular components:

```
GSSoC-Verification-Bot/
├── bot.py                   # Main bot file (entry point)
├── excel_handler.py         # Excel data processing module
├── commands/                # Command modules
│   ├── __init__.py          # Package initialization
│   ├── about.py             # About command
│   ├── moderation.py        # Moderation commands (ban, kick, etc.)
│   └── ...                  # Other command modules
├── Verification_Module/     # Verification functionality
│   ├── __init__.py          # Package initialization
│   └── verify.py            # Verification commands and logic
├── welcome_messages.json    # Stores welcome message data
├── verification_loga.json   # Verification logs
├── username_updates.json    # Username update logs
└── failed_attempts.json     # Failed verification attempts
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GSSoC-Verification-Bot.git
cd GSSoC-Verification-Bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:
```
DISCORD_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_guild_id
DISCORD_VERIFICATION_CHANNEL_ID=verification_channel_id
AUTO_ASSIGNED_ROLE_ID=unverified_role_id
WELCOME_CHANNEL_ID=welcome_channel_id
LOG_CHANNEL_ID=log_channel_id

# Role IDs
ROLE_CONTRI=contributor_role_id
ROLE_CONTRI_WOB=wob_contributor_role_id
ROLE_CA=campus_ambassador_role_id
ROLE_CA_WOB=wob_campus_ambassador_role_id
ROLE_MENTOR=mentor_role_id
ROLE_MENTOR_WOB=wob_mentor_role_id
ROLE_PA=project_admin_role_id
ROLE_PA_WOB=wob_project_admin_role_id
```

4. Create the Excel sheets directory:
```bash
mkdir -p Excel-Sheets
```

5. Add your Excel sheets with user data to the `Excel-Sheets` directory.

## Usage

Run the bot:
```bash
python bot.py
```

## Adding New Commands

To add a new command, create a new file in the `commands` directory:

```python
# commands/new_command.py
import discord
import os

def setup(bot, tree, bot_data, admin_ids, homies):
    guild_id = int(os.getenv('DISCORD_GUILD_ID'))
    
    @tree.command(
        name="command_name", 
        description="Command description", 
        guild=discord.Object(id=guild_id)
    )
    async def command_name(interaction: discord.Interaction):
        # Command logic here
        await interaction.response.send_message("Response")
```

## License

This project is licensed under the MIT License. 