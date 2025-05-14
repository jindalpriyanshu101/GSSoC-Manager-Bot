import discord
from discord.ext import commands, tasks
import os
import importlib
import sys
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from excel_handler import load_excel_data

# Load environment variables
load_dotenv()

# Get environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))
VERIFICATION_CHANNEL_ID = int(os.getenv('DISCORD_VERIFICATION_CHANNEL_ID'))
AUTO_ASSIGNED_ROLE_ID = int(os.getenv('AUTO_ASSIGNED_ROLE_ID'))
WELCOME_CHANNEL_ID = int(os.getenv('WELCOME_CHANNEL_ID'))
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', '1292522424054710302'))

# Role IDs
Role_contri = int(os.getenv('ROLE_CONTRI'))
Role_contri_wob = int(os.getenv('ROLE_CONTRI_WOB'))
Role_ca = int(os.getenv('ROLE_CA'))
Role_ca_wob = int(os.getenv('ROLE_CA_WOB'))
Role_mentor = int(os.getenv('ROLE_MENTOR'))
Role_mentor_wob = int(os.getenv('ROLE_MENTOR_WOB'))
Role_pa = int(os.getenv('ROLE_PA'))
Role_pa_wob = int(os.getenv('ROLE_PA_WOB'))

# Permission IDs
ADMIN_IDS = [438560155639087105]
HOMIES = []

# Funny responses
APSHABD = ["Na raha jara to te? Karu guddi laal?",
           "Wah beta wah, kya baat hai. Chle ja shanti see",
           "Abe kya bola be tune? hosh meto haina chewwww :skull:",
           "Kya bol raha hai be?",
           "Wah beta, lagta hai khurak lekr hi manega?",
           "Nikal l.., pehli fursat me nikal",
           "Mat kr koshish, pela jayga tu",
           "B--, chup chap apna kaam kr",
           "Bade manhus irade hai apke, ese me bot kre to kya kre?"]

# Constants
ROLE_PRIORITY = ['Project Admin Wob', 
                 'Project Admin',
                 'Mentor Wob', 
                 'Mentor', 
                 'Campus Ambassador Wob',
                 'Campus Ambassador',  
                 'Contributor Wob', 
                 'Contributor']

ROLE_PRIORITY_LOWER = ['project admin', 
                       'mentor', 
                       'campus ambassador', 
                       'contributor',
                       'contributer', 
                       'pa', 
                       'ca', 
                       'contri', 
                       'CA', 
                       'PA']

# File paths
welcome_log = 'welcome_messages.json'

# Set up intents and bot
intents = discord.Intents.all()
intents.message_content = True  # Explicitly enable message content intent
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

# Print confirmation of intents
print("Bot setup with the following intents:")
print(f"- Message Content: {intents.message_content}")
print(f"- Members: {intents.members}")
print(f"- Guilds: {intents.guilds}")

# Shared data storage
bot_data = {
    'excel_data': {},
    'welcome_messages': {},
    'cached_unverified_members': [],
    'constants': {
        'ROLE_PRIORITY': ROLE_PRIORITY,
        'ROLE_PRIORITY_LOWER': ROLE_PRIORITY_LOWER,
        'APSHABD': APSHABD
    },
    'role_ids': {
        'Contributor': Role_contri,
        'Contributor | Wob': Role_contri_wob,
        'Campus Ambassador': Role_ca,
        'CA | Wob': Role_ca_wob,
        'Mentor': Role_mentor,
        'Mentor | Wob': Role_mentor_wob,
        'Project Admin': Role_pa,
        'PA | Wob': Role_pa_wob,
        'AUTO_ASSIGNED': AUTO_ASSIGNED_ROLE_ID
    }
}

# Functions for welcome message handling
def load_welcome_log():
    if os.path.exists(welcome_log) and os.stat(welcome_log).st_size > 0:
        try:
            with open(welcome_log, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_welcome_log(welcome_messages):
    with open(welcome_log, 'w') as f:
        json.dump(welcome_messages, f, indent=4)

@bot.event
async def on_ready():
    # Load Excel data into bot_data
    bot_data['excel_data'] = load_excel_data()
    bot_data['welcome_messages'] = load_welcome_log()
    
    print(f'{bot.user} has connected to Discord!')
    
    # Set bot activity
    activity = discord.Activity(
        type=discord.ActivityType.watching, 
        name="Verification process for GSSoC'24"
    )
    await bot.change_presence(activity=activity)
    
    # Sync slash commands
    try:
        # Sync commands globally and to the guild
        await bot.tree.sync()  # For slash/hybrid commands globally
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))  # For guild-specific commands
        print(f'Synced {len(synced)} commands successfully.')
    except Exception as e:
        print(f'Error syncing commands: {e}')
        import traceback
        traceback.print_exc()

    # Start tasks
    cleanup_welcome_messages.start()
    
    # Start verification module tasks
    try:
        import Verification_Module.verify as verify_module
        verify_module.start_background_tasks()
        print("Started verification module background tasks")
    except Exception as e:
        print(f"Error starting verification tasks: {e}")
        import traceback
        traceback.print_exc()
    
    print(f'Bot is ready, logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, id=AUTO_ASSIGNED_ROLE_ID)
    if role:
        await member.add_roles(role)
        print(f"Assigned unverified role to {member.name}")

        welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if welcome_channel:
            welcome_message = await welcome_channel.send(
                f"Welcome to the server, {member.mention}! To get access to GSSoC, please verify your selection by using the command `/verify registered-email-id`"
            )
            bot_data['welcome_messages'][member.id] = {
                "message_id": welcome_message.id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            save_welcome_log(bot_data['welcome_messages'])
        else:
            print(f"Failed to find the welcome channel {WELCOME_CHANNEL_ID}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        # Get command signature and description
        command = ctx.command
        signature = command.signature
        description = command.description or "No description available"
        
        # Create an embed for the error
        embed = discord.Embed(
            title=f"Command: {ctx.prefix}{command.name}",
            description=f"{description}",
            color=discord.Color.red()
        )
        
        # Add the correct usage field
        embed.add_field(
            name="Usage",
            value=f"`{ctx.prefix}{command.name} {signature}`",
            inline=False
        )
        
        # Add the specific error message
        embed.add_field(
            name="Error",
            value=f"Missing required argument: `{error.param.name}`",
            inline=False
        )
        
        # Add examples if we want to add them for specific commands later
        # if hasattr(command, "examples") and command.examples:
        #     embed.add_field(name="Examples", value="\n".join(command.examples), inline=False)
        
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        # Similar to MissingRequiredArgument but for incorrect argument types
        command = ctx.command
        signature = command.signature
        
        embed = discord.Embed(
            title=f"Command: {ctx.prefix}{command.name}",
            description=f"You provided an invalid argument for this command.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Usage",
            value=f"`{ctx.prefix}{command.name} {signature}`", 
            inline=False
        )
        
        embed.add_field(
            name="Error",
            value=str(error),
            inline=False
        )
        
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You don't have the required permissions: {', '.join(error.missing_permissions)}")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"I don't have the required permissions: {', '.join(error.missing_permissions)}")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command cannot be used in private messages.")
    else:
        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@tasks.loop(minutes=30)
async def cleanup_welcome_messages():
    now = datetime.now(timezone.utc)
    welcome_messages = bot_data['welcome_messages']
    stale_messages = {member_id: data for member_id, data in welcome_messages.items()
                      if now - datetime.fromisoformat(data["timestamp"]) > timedelta(hours=1)}

    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        for member_id, data in stale_messages.items():
            try:
                message_id = data["message_id"]
                message = await welcome_channel.fetch_message(message_id)
                await message.delete()
                del welcome_messages[member_id]
            except discord.NotFound:
                print(f"Message {message_id} not found.")
        save_welcome_log(welcome_messages)
        bot_data['welcome_messages'] = welcome_messages

# Load command modules
def load_commands():
    # Create necessary directories if they don't exist
    os.makedirs("commands", exist_ok=True)
    os.makedirs("Verification_Module", exist_ok=True)
    
    # Create __init__.py files to make directories importable
    for dir_path in ["commands", "Verification_Module"]:
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Module initialization file\n")
    
    # Load verification module
    try:
        import Verification_Module.verify as verify_module
        verify_module.setup(bot, tree, bot_data, GUILD_ID, VERIFICATION_CHANNEL_ID)
        print("Loaded verification module")
    except Exception as e:
        print(f"Error loading verification module: {e}")
        import traceback
        traceback.print_exc()
    
    # Load individual commands from commands folder
    if os.path.exists("commands"):
        command_files = [f[:-3] for f in os.listdir("commands") 
                        if f.endswith(".py") and not f.startswith("__")]
        
        for command in command_files:
            try:
                module = importlib.import_module(f"commands.{command}")
                if hasattr(module, 'setup'):
                    module.setup(bot, tree, bot_data, ADMIN_IDS, HOMIES)
                    print(f"Loaded command module: {command}")
            except Exception as e:
                print(f"Error loading command module {command}: {e}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):

    # Handle errors from application (slash) commands
    # Unwrap the error if it's wrapped in a CommandInvokeError
    error = getattr(error, "original", error)
    
    if isinstance(error, commands.MissingRequiredArgument):
        command_name = interaction.command.name if interaction.command else "Unknown command"
        
        embed = discord.Embed(
            title=f"Command: /{command_name}",
            description="Missing a required argument",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Error",
            value=f"Missing required argument: `{error.param.name}`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    elif isinstance(error, commands.BadArgument):
        command_name = interaction.command.name if interaction.command else "Unknown command"
        
        embed = discord.Embed(
            title=f"Command: /{command_name}",
            description="You provided an invalid argument",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Error",
            value=str(error),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    elif isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message(
            f"You don't have the required permissions: {', '.join(error.missing_permissions)}",
            ephemeral=True
        )
    elif isinstance(error, commands.BotMissingPermissions):
        await interaction.response.send_message(
            f"I don't have the required permissions: {', '.join(error.missing_permissions)}",
            ephemeral=True
        )
    elif isinstance(error, commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds.",
            ephemeral=True
        )
    elif isinstance(error, commands.NoPrivateMessage):
        await interaction.response.send_message(
            "This command cannot be used in private messages.",
            ephemeral=True
        )
    else:
        # Log the error
        print(f"Ignoring exception in app command:", file=sys.stderr)
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        
        # Notify the user
        if interaction.response.is_done():
            await interaction.followup.send(
                "An error occurred while executing the command.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "An error occurred while executing the command.",
                ephemeral=True
            )

if __name__ == "__main__":
    load_commands()
    bot.run(TOKEN)
