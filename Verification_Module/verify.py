import discord 
import json
from discord.ext import commands, tasks
from excel_handler import get_roles_for_email, load_excel_data
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# File paths
attempts_log = 'failed_attempts.json'
verification_log = 'verification_loga.json'
welcome_log = 'welcome_messages.json'
username_log = 'username_updates.json'

# Global variables for module
bot = None
tree = None
bot_data = None
guild_id = None
verification_channel_id = None

def setup(bot_instance, tree_instance, bot_data_dict, guild_id_value, verification_channel_id_value):
    global bot, tree, bot_data, guild_id, verification_channel_id
    
    # Initialize global variables
    bot = bot_instance
    tree = tree_instance
    bot_data = bot_data_dict
    guild_id = guild_id_value
    verification_channel_id = verification_channel_id_value
    
    # Load environment variables
    load_dotenv()
    register_commands()

    print("Verification module setup complete")

def register_commands():
        
    # Register the verify command
    @bot.hybrid_command(
        name="verify", 
        description="Verify your registered email id to get access."
    )
    @commands.guild_only()
    async def verify(ctx, email: str):
        # For prefix command
        if not isinstance(ctx, discord.Interaction):
            interaction = ctx.interaction
            
            # Only allow command in verification channel
            if ctx.channel.id != verification_channel_id:
                await ctx.send(f"This command can only be used in <#{verification_channel_id}>.", ephemeral=True)
                return
                
            await verify_user(interaction, email)
        else:
            # For slash command
            await verify_user(ctx, email)
    
    # Register the admin verify command
    @bot.hybrid_command(
        name="adminverify", 
        description="Admin command to verify a user by providing their email."
    )
    @commands.guild_only()
    async def adminverify(ctx, user: discord.Member, email: str):
        # For prefix command
        if not isinstance(ctx, discord.Interaction):
            interaction = ctx.interaction
            await admin_verify_user(interaction, user, email)
        else:
            # For slash command
            await admin_verify_user(ctx, user, email)
    
    @bot.hybrid_command(
        name="cacheunverified", 
        description="Cache members needing reassignment."
    )
    @commands.guild_only()
    async def cacheunverified(ctx):
        # For prefix command
        if not isinstance(ctx, discord.Interaction):
            interaction = ctx.interaction
            await cache_unverified_members(interaction)
        else:
            # For slash command
            await cache_unverified_members(ctx)

# Start tasks in this function to be called from on_ready
def start_background_tasks():
    cleanup_welcome_messages.start()

# Utility functions
def load_attempts_log():
    if os.path.exists(attempts_log) and os.stat(attempts_log).st_size > 0:
        try:
            with open(attempts_log, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_attempts_log(failed_attempts):
    with open(attempts_log, 'w') as f:
        json.dump(failed_attempts, f, indent=4)

def load_verification_log():
    if os.path.exists(verification_log) and os.stat(verification_log).st_size > 0:
        try:
            with open(verification_log, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_verification_log(log_entry):
    logs = load_verification_log()
    logs.append(log_entry)
    with open(verification_log, 'w') as f:
        json.dump(logs, f, indent=4)

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

def load_username_log():
    if os.path.exists(username_log) and os.stat(username_log).st_size > 0:
        try:
            with open(username_log, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_username_log(log_entry):
    logs = load_username_log()
    logs.append(log_entry)
    with open(username_log, 'w') as f:
        json.dump(logs, f, indent=4)

def log_username_update(member, email, oldname, newname):
    log_entry = {
        "discordusername": member.name,
        "discordid": member.id,
        "email": email,
        "oldname": oldname,
        "newname": newname,
        "time": datetime.now(timezone.utc).isoformat() 
    }
    save_username_log(log_entry)

# Event handlers for member join (will be registered in the bot.py file)
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, id=bot_data['role_ids']['AUTO_ASSIGNED'])
    if role:
        await member.add_roles(role)
        print(f"Assigned unverified role to {member.name}")

        welcome_channel = bot.get_channel(int(os.getenv('WELCOME_CHANNEL_ID')))
        if welcome_channel:
            welcome_message = await welcome_channel.send(
                f"Welcome to the server, {member.mention}! To get access to GSSoC, please verify your selection by using the command `/verify registered-email-id`"
            )
            
            welcome_messages = bot_data.get('welcome_messages', {})
            welcome_messages[member.id] = {
                "message_id": welcome_message.id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            bot_data['welcome_messages'] = welcome_messages
            save_welcome_log(welcome_messages)
        else:
            print(f"Failed to find the welcome channel {int(os.getenv('WELCOME_CHANNEL_ID'))}")

# Command implementations
async def verify_user(interaction: discord.Interaction, email: str):
    member = interaction.user
    auto_assigned_role = discord.utils.get(member.guild.roles, id=bot_data['role_ids']['AUTO_ASSIGNED'])

    if interaction.channel.id != verification_channel_id:
        await interaction.response.send_message(f"This command can only be used in <#{verification_channel_id}>.", ephemeral=True)
        return

    role_names = get_roles_for_email(email, bot_data['excel_data'])

    if not role_names:
        await interaction.response.send_message("This email is not in our records. Contact a moderator in case of any errors.", ephemeral=True)
        failed_attempts = load_attempts_log()
        failed_attempts[str(member.id)] = email
        save_attempts_log(failed_attempts)
        return

    # Get roles to assign
    roles_to_assign = []
    for name in role_names:
        role_id = bot_data['role_ids'].get(name)
        if role_id:
            role = discord.utils.get(interaction.guild.roles, id=role_id)
            if role:
                roles_to_assign.append(role)

    if roles_to_assign:
        await member.add_roles(*roles_to_assign)
        role_names_str = ", ".join(role_names)
        
        # Find highest priority role
        highest_role = None
        for role in bot_data['constants']['ROLE_PRIORITY']:
            if role in role_names:
                highest_role = role
                break

        # Remove auto assigned role if present
        if auto_assigned_role in member.roles:
            await member.remove_roles(auto_assigned_role)
            print(f"Removed auto-assigned role from {member.name}")

        # Format the display name
        display_name = member.display_name
        
        # Remove existing roles from the display name
        for role in bot_data['constants']['ROLE_PRIORITY'] + bot_data['constants']['ROLE_PRIORITY_LOWER']:
            # Check for " | ROLE" pattern
            pattern_1 = f" | {role}"
            pattern_2 = f"|{role}"

            if pattern_1 in display_name:
                display_name = display_name.replace(pattern_1, "").strip()
            elif pattern_2 in display_name:
                display_name = display_name.replace(pattern_2, "").strip()
            
            # Check for standalone role
            if role in display_name.split(" "):
                display_name = display_name.replace(role, "").strip()

        # Create new nickname with appropriate formatting
        new_nickname = f"{display_name} | {highest_role}"
        if len(new_nickname) > 32:
            excess_length = len(new_nickname) - 32
            truncated_display_name = display_name[:-excess_length]
            display_name = truncated_display_name

            if highest_role == "Campus Ambassador":
                new_nickname = f"{display_name} | CA"
            elif highest_role == "CA | Wob":
                new_nickname = f"{display_name} | CA | WoB"
            elif highest_role == "Contributor | Wob":
                new_nickname = f"{display_name} | Contri | WoB"
            elif highest_role == "Mentor | Wob":
                new_nickname = f"{display_name} | Mentor | WoB"
            elif highest_role == "PA | Wob":
                new_nickname = f"{display_name} | PA | WoB"
            else:
                excess_length = len(new_nickname) - 32
                truncated_display_name = display_name[:-excess_length]
                new_nickname = f"{truncated_display_name} | {highest_role}"

        # Send appropriate welcome message
        if "Wob" in new_nickname or "WoB" in new_nickname:
            await interaction.response.send_message(
                f":tada: Congratulations! {member.mention} :tada:, you're selected as `{role_names_str}` for Winter Of Blockchain 2024.", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f":tada: Congratulations! {member.mention} :tada:, you're selected as `{role_names_str}` for GSSoC'24 Extended.", 
                ephemeral=True
            )

        # Update nickname if not the server owner
        if member != interaction.guild.owner:
            try:
                old_display_name = member.display_name
                await member.edit(nick=new_nickname)
                print(f"Updated nickname for {old_display_name} to {new_nickname}")
                
                # Log the username update
                log_username_update(member, email, old_display_name, new_nickname)
                
                await interaction.followup.send(
                    f"{member.mention} Your username has been updated to `{new_nickname}` as per Guidelines. "
                    f"You are free to change it, but please ensure that **{highest_role}** remains part of your display name.",
                    ephemeral=True
                )
            except discord.Forbidden:
                print(f"Failed to change nickname for {member.name} due to missing permissions.")

        # Delete welcome message if exists
        welcome_messages = bot_data.get('welcome_messages', {})
        if member.id in welcome_messages:
            welcome_channel = bot.get_channel(int(os.getenv('WELCOME_CHANNEL_ID')))
            if welcome_channel:
                message_id = welcome_messages[member.id]["message_id"]
                try:
                    welcome_message = await welcome_channel.fetch_message(message_id)
                    await welcome_message.delete()
                    del welcome_messages[member.id]
                    bot_data['welcome_messages'] = welcome_messages
                    save_welcome_log(welcome_messages)
                except discord.NotFound:
                    print(f"Welcome message {message_id} not found.")

        # Log successful verification
        log_entry = {
            "discordusername": member.name,
            "discordid": member.id,
            "email": email,
            "roles": role_names,
            "time": datetime.now(timezone.utc).isoformat()
        }
        save_verification_log(log_entry)

    else:
        await interaction.response.send_message(
            f"Sorry, we couldn't verify your email at this time.", 
            ephemeral=True
        )

async def admin_verify_user(interaction: discord.Interaction, user: discord.Member, email: str):
    # Admin IDs from environment
    admin_ids = [int(id) for id in os.getenv('ADMIN_IDS', '438560155639087105,737927879052099595').split(',')]
    
    # Check admin permissions
    if interaction.user.id not in admin_ids:
        await interaction.response.send_message(
            "You do not have permission to use this command.", 
            ephemeral=True
        )
        return
    
    # Get auto-assigned role
    auto_assigned_role = discord.utils.get(user.guild.roles, id=bot_data['role_ids']['AUTO_ASSIGNED'])
    
    # Check email in records
    role_names = get_roles_for_email(email, bot_data['excel_data'])
    
    if not role_names:
        await interaction.response.send_message(
            f"The email `{email}` is not in our records. Please contact a moderator.", 
            ephemeral=True
        )
        failed_attempts = load_attempts_log()
        failed_attempts[str(user.id)] = email
        save_attempts_log(failed_attempts)
        return
    
    # Get roles to assign
    roles_to_assign = []
    for name in role_names:
        role_id = bot_data['role_ids'].get(name)
        if role_id:
            role = discord.utils.get(interaction.guild.roles, id=role_id)
            if role:
                roles_to_assign.append(role)
    
    if roles_to_assign:
        # Assign roles
        await user.add_roles(*roles_to_assign)
        role_names_str = ", ".join(role_names)
        await interaction.response.send_message(
            f":tada: {user.mention} has been successfully verified as `{role_names_str}`.", 
            ephemeral=True
        )
        
        # Remove auto-assigned role if present
        if auto_assigned_role and auto_assigned_role in user.roles:
            await user.remove_roles(auto_assigned_role)
            print(f"Removed auto-assigned role from {user.name}")
        
        # Find highest priority role
        highest_role = None
        for role in bot_data['constants']['ROLE_PRIORITY']:
            if role in role_names:
                highest_role = role
                break
        
        # Format nickname
        display_name = user.display_name
        
        # Remove existing roles from display name
        for role in bot_data['constants']['ROLE_PRIORITY'] + bot_data['constants']['ROLE_PRIORITY_LOWER']:
            # Check for " | ROLE" pattern
            pattern_1 = f" | {role}"
            pattern_2 = f"|{role}"
            
            if pattern_1 in display_name:
                display_name = display_name.replace(pattern_1, "").strip()
            elif pattern_2 in display_name:
                display_name = display_name.replace(pattern_2, "").strip()
            
            # Check for standalone role
            if role in display_name.split(" "):
                display_name = display_name.replace(role, "").strip()
        
        # Create new nickname
        new_nickname = f"{display_name} | {highest_role}"
        if len(new_nickname) > 32:
            if highest_role == "Campus Ambassador":
                new_nickname = f"{display_name} | CA"
            else:
                excess_length = len(new_nickname) - 32
                truncated_display_name = display_name[:-excess_length]
                new_nickname = f"{truncated_display_name} | {highest_role}"
        
        # Update nickname if not server owner
        if user != interaction.guild.owner:
            try:
                old_display_name = user.display_name
                await user.edit(nick=new_nickname)
                print(f"Updated nickname for {old_display_name} to {new_nickname}")
                
                # Log username update
                log_username_update(user, email, old_display_name, new_nickname)
                
                await interaction.followup.send(
                    f"{user.mention} Your username has been updated to `{new_nickname}` as per GSSoC guidelines.",
                    ephemeral=True
                )
            except discord.Forbidden:
                print(f"Failed to change nickname for {user.name} due to missing permissions.")
        
        # Log successful verification
        log_entry = {
            "discordusername": user.name,
            "discordid": user.id,
            "email": email,
            "roles": role_names,
            "time": datetime.now(timezone.utc).isoformat()
        }
        save_verification_log(log_entry)
    
    else:
        await interaction.response.send_message(
            f"Sorry, we couldn't verify the email `{email}` at this time.", 
            ephemeral=True
        )

async def cache_unverified_members(interaction: discord.Interaction):
    # Admin IDs from environment
    admin_ids = [int(id) for id in os.getenv('ADMIN_IDS', '438560155639087105,737927879052099595').split(',')]
    
    # Check admin permissions
    if interaction.user.id not in admin_ids:
        await interaction.response.send_message(
            "You do not have permission to use this command.", 
            ephemeral=False
        )
        return
    
    bot_data['cached_unverified_members'] = []
    
    try:
        # Find members with few roles
        for member in interaction.guild.members:
            if len(member.roles) <= 2:  # Default role + possibly one more
                bot_data['cached_unverified_members'].append(member)
        
        await interaction.response.send_message(
            f"Successfully cached {len(bot_data['cached_unverified_members'])} unverified member(s).", 
            ephemeral=False
        )
    except Exception as e:
        print(e)
        await interaction.response.send_message(
            f"An error occurred: {e}", 
            ephemeral=False
        )

@tasks.loop(minutes=30)
async def cleanup_welcome_messages():
    now = datetime.now(timezone.utc)
    welcome_messages = bot_data.get('welcome_messages', {})
    stale_messages = {member_id: data for member_id, data in welcome_messages.items()
                     if now - datetime.fromisoformat(data["timestamp"]) > timedelta(hours=1)}
    
    welcome_channel = bot.get_channel(int(os.getenv('WELCOME_CHANNEL_ID')))
    if welcome_channel:
        for member_id, data in stale_messages.items():
            try:
                message_id = data["message_id"]
                message = await welcome_channel.fetch_message(message_id)
                await message.delete()
                del welcome_messages[member_id]
            except discord.NotFound:
                print(f"Message {message_id} not found.")
        
        bot_data['welcome_messages'] = welcome_messages
        save_welcome_log(welcome_messages)
