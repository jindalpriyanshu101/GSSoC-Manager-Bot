# GSSoC Manager Bot

A comprehensive Discord bot designed for the `GirlScript Summer of Code (GSSoC)` and `Winter of Blockchain (WoB)` communities. This bot provides automated user verification, role management, moderation tools, and administrative capabilities to streamline community management.

## Features

### Core Verification System
- **Email-based verification**: Automated user verification using registered email addresses from Excel data sources
- **Multi-tier role assignment**: Supports Contributors, Campus Ambassadors, Mentors, and Project Admins for both GSSoC and WoB programs
- **Role hierarchy management**: Intelligent role priority system with conflict resolution
- **Failed attempt tracking**: Comprehensive logging of verification failures for security monitoring
- **Username standardization**: Automatic username formatting to maintain community standards

### Moderation Tools
- **User management**: Ban, kick, and timeout commands with configurable durations and reason logging
- **Warning system**: Progressive warning tracking with persistent storage and escalation capabilities
- **Message cleanup**: Bulk message deletion and channel management tools
- **Permission-based access**: Role-based command restrictions for administrative functions

### Channel Management
- **Dynamic channel creation**: Create text channels with customizable settings including slowmode, NSFW flags, and topics
- **Category organization**: Organize channels within specific categories
- **Bulk operations**: Mass channel management and configuration updates

### Data Management and Caching
- **Excel integration**: Supports multiple Excel data sources for different participant categories
- **In-memory caching**: Optimized data loading with startup caching for improved performance
- **Unverified member caching**: Administrative tools to identify and manage users requiring verification
- **Persistent logging**: JSON-based storage for verification logs, welcome messages, and user activities

### Administrative Features
- **Welcome automation**: Automated welcome messages with cleanup tasks for new members
- **Logging system**: Comprehensive action logging to designated channels
- **Background tasks**: Automated maintenance operations including message cleanup
- **Environment configuration**: Extensive configuration management via environment variables

## Available Commands

### Verification Commands
- `/verify <email>` - Verify user registration with email address
- `/adminverify <user> <email>` - Administrative verification for specific users
- `/cacheunverified` - Cache members requiring verification (admin only)

### Moderation Commands
- `/ban <user> [reason]` - Ban user from server with optional reason
- `/kick <user> [reason]` - Remove user from server
- `/timeout <user> <duration> <unit> [reason]` - Temporary restriction (minutes/hours/days)
- `/warn <user> [reason]` - Issue warning to user with tracking
- `/warnings <user>` - View user's warning history
- `/clearwarnings <user>` - Clear user's warning record

### Role Management
- `/addrole <user> <role> [reason]` - Assign role to user
- `/removerole <user> <role> [reason]` - Remove role from user

### Channel Management
- `/createchannel <name>` - Create new text channel with optional configuration
- `/deletechannel <channel>` - Remove specified channel
- `/cleanup <amount>` - Delete specified number of messages

### Utility Commands
- `/about` - Display bot information and developer details

## Data Sources

The bot integrates with multiple Excel files located in the `Excel-Sheets` directory:

```
Excel-Sheets/
├── contributor_Data.xlsx        # GSSoC Contributors
├── contributors_wob.xlsx        # WoB Contributors  
├── CA.xlsx                      # Campus Ambassadors (Primary)
├── CA2.xlsx                     # Campus Ambassadors (Extended)
├── CA_wob.xlsx                  # WoB Campus Ambassadors
├── MENTOR.xlsx                  # GSSoC Mentors
├── MENTORS_wob.xlsx            # WoB Mentors
├── PA.xlsx                      # GSSoC Project Admins
└── PA_wob.xlsx                  # WoB Project Admins
```

## Project Structure

```
GSSoC-Manager-Bot/
├── bot.py                      # Main bot entry point and event handlers
├── bot-test.py                 # Development testing version
├── excel_handler.py            # Excel data processing and role assignment logic
├── requirements.txt            # Python dependencies
├── commands/                   # Modular command implementations
│   ├── __init__.py
│   ├── about.py               # Bot information command
│   ├── channel.py             # Channel management commands
│   ├── moderation.py          # Ban, kick, timeout commands
│   ├── role.py                # Role assignment commands
│   ├── timeout.py             # User timeout functionality
│   └── warn.py                # Warning system implementation
├── Verification_Module/        # Core verification system
│   ├── __init__.py
│   └── verify.py              # Email verification and user management
├── Excel-Sheets/              # User data sources (not tracked in git)
├── Logos/                     # Bot assets and community logos
└── Data Files (auto-generated):
    ├── welcome_messages.json   # Welcome message tracking
    ├── verification_loga.json  # Verification activity logs
    ├── username_updates.json   # Username change history
    ├── failed_attempts.json    # Failed verification attempts
    └── warnings.json           # User warning records
```

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Discord application with bot token
- Excel files with participant data

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/jindalpriyanshu101/GSSoC-Manager-Bot.git
cd GSSoC-Manager-Bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Configuration**
Create a `.env` file in the root directory with the following variables:

```env
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_guild_id
DISCORD_VERIFICATION_CHANNEL_ID=verification_channel_id
WELCOME_CHANNEL_ID=welcome_channel_id
LOG_CHANNEL_ID=log_channel_id

# Role Configuration
AUTO_ASSIGNED_ROLE_ID=unverified_role_id
ROLE_CONTRI=contributor_role_id
ROLE_CONTRI_WOB=wob_contributor_role_id
ROLE_CA=campus_ambassador_role_id
ROLE_CA_WOB=wob_campus_ambassador_role_id
ROLE_MENTOR=mentor_role_id
ROLE_MENTOR_WOB=wob_mentor_role_id
ROLE_PA=project_admin_role_id
ROLE_PA_WOB=wob_project_admin_role_id

# Administrative Configuration
ADMIN_IDS=comma_separated_admin_user_ids
```

4. **Data Setup**
```bash
mkdir Excel-Sheets
# Add your Excel files to the Excel-Sheets directory
```

5. **Run the bot**
```bash
python bot.py
```

## Technical Details

### Dependencies
- **discord.py**: Discord API integration with full feature support
- **pandas**: Excel data processing and manipulation
- **python-dotenv**: Environment variable management
- **openpyxl**: Excel file reading capabilities
- **aiosmtplib**: Asynchronous email functionality

### Architecture
- **Modular design**: Separated command modules for maintainability
- **Hybrid commands**: Support for both slash commands and traditional prefix commands
- **Event-driven**: Utilizes Discord.py event system for real-time responses
- **Asynchronous operations**: Non-blocking operations for optimal performance
- **Error handling**: Comprehensive error management with user-friendly feedback

### Performance Features
- **Startup caching**: Excel data loaded into memory at bot initialization
- **Background tasks**: Automated cleanup and maintenance operations
- **Optimized queries**: Efficient role and permission checking
- **Minimal API calls**: Reduced Discord API usage through intelligent caching

## Development and Extensibility

### Adding New Commands

Commands are organized in the `commands/` directory. To add a new command:

1. Create a new Python file in the `commands/` directory
2. Implement the setup function with command logic
3. The bot automatically loads all command modules

Example command structure:
```python
# commands/example.py
import discord
import os
from discord.ext import commands

def setup(bot, tree, bot_data, admin_ids, homies):
    guild_id = int(os.getenv('DISCORD_GUILD_ID'))
    
    @bot.hybrid_command(
        name="example", 
        description="Example command description"
    )
    @commands.guild_only()
    async def example_command(ctx, parameter: str):
        # Command implementation
        await ctx.send(f"Example response: {parameter}")
```

### Data Storage
- **JSON files**: Used for logging and temporary data storage
- **Excel integration**: Primary data source for user verification
- **Environment variables**: Configuration management
- **In-memory caching**: Performance optimization for frequently accessed data

### Security Features
- **Permission-based access**: Commands restricted based on Discord permissions
- **Admin verification**: Special administrative command access control
- **Audit logging**: Comprehensive action logging for security monitoring
- **Rate limiting**: Built-in Discord.py rate limiting for API protection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Support

For issues, questions, or feature requests:
- Create an issue on GitHub
- Contact me [here](mailto:priyanshujindal101@gmail.com)
- Review the documentation and command help

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

Developed for the `GirlScript Summer of Code (GSSoC - 2024)` and `Winter of Blockchain (WoB - 2024)` communities to enhance community management and user experience. by [Priyanshu](https://github.com/jindalpriyanshu101)
