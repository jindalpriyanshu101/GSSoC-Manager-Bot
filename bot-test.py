import discord 
import json
from discord.ext import commands, tasks
from excel_handler import get_roles_for_email, load_excel_data
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))
VERIFICATION_CHANNEL_ID = int(os.getenv('DISCORD_VERIFICATION_CHANNEL_ID'))

Role_contri = int(os.getenv('ROLE_CONTRI'))
Role_ca = int(os.getenv('ROLE_CA'))
Role_mentor = int(os.getenv('ROLE_MENTOR'))
Role_pa = int(os.getenv('ROLE_PA'))
AUTO_ASSIGNED_ROLE_ID = int(os.getenv('AUTO_ASSIGNED_ROLE_ID'))
WELCOME_CHANNEL_ID = int(os.getenv('WELCOME_CHANNEL_ID'))

ROLE_PRIORITY = ['Project Admin', 'Mentor', 'Campus Ambassador', 'Contributor']
ROLE_PRIORITY_LOWER = ['project admin', 'mentor', 'campus ambassador', 'contributor', 'pa', 'ca', 'contri']

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

attempts_log = 'failed_attempts.json'
verification_log = 'verification_loga.json'
welcome_log = 'welcome_messages.json'
username_log = 'username_updates.json'  # New log file for username updates
excel_data = {}
welcome_messages = {}

def load_attempts_log():
    if os.path.exists(attempts_log) and os.stat(attempts_log).st_size > 0:
        try:
            with open(attempts_log, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

failed_attempts = load_attempts_log()

def save_attempts_log():
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

# New functions for username update log
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
        "time": datetime.now(timezone.utc).isoformat()  # Time of the update
    }
    save_username_log(log_entry)

@bot.event
async def on_ready():
    global excel_data
    global welcome_messages

    excel_data = load_excel_data()
    welcome_messages = load_welcome_log()  # Load welcome messages from file

    activity = discord.Activity(type=discord.ActivityType.watching, name="Verification process for GSSoC'24")
    await bot.change_presence(activity=activity)    
    
    print(f'{bot.user} has connected to Discord!')

    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f'Synced {len(synced)} commands successfully.')
    except Exception as e:
        print(f'Error syncing commands: {e}')

    cleanup_welcome_messages.start()

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
            welcome_messages[member.id] = {
                "message_id": welcome_message.id,
                "timestamp": datetime.now(timezone.utc).isoformat()  # Store with timezone-aware UTC timestamp
            }
            save_welcome_log(welcome_messages)  # Save to file
        else:
            print(f"Failed to find the welcome channel {WELCOME_CHANNEL_ID}")

@tree.command(name="verify", description="Verify your registered email id to get access.", guild=discord.Object(id=GUILD_ID))
async def verify(interaction: discord.Interaction, email: str):
    member = interaction.user
    auto_assigned_role = discord.utils.get(member.guild.roles, id=AUTO_ASSIGNED_ROLE_ID)

    if interaction.channel.id != VERIFICATION_CHANNEL_ID:
        await interaction.response.send_message("This command can only be used in <#{VERIFICATION_CHANNEL_ID}>.", ephemeral=True)
        return

    role_names = get_roles_for_email(email, excel_data)

    if not role_names:
        await interaction.response.send_message("This email is not in our records. Contact a moderator in case of any errors.", ephemeral=True)
        failed_attempts[str(member.id)] = email
        save_attempts_log()
        return

    role_ids = {
        'Contributor': Role_contri,
        'Campus Ambassador': Role_ca,
        'Mentor': Role_mentor,
        'Project Admin': Role_pa
    }

    roles_to_assign = [discord.utils.get(interaction.guild.roles, id=role_ids[name]) for name in role_names]

    if roles_to_assign:
        await member.add_roles(*roles_to_assign)
        role_names_str = ", ".join(role_names)
        await interaction.response.send_message(f":tada: Congratulations! {member.mention} :tada:, you're selected as `{role_names_str}` for GSSoC'24 Extended.", ephemeral=True)

        highest_role = None
        for role in ROLE_PRIORITY:
            if role in role_names:
                highest_role = role
                break

        if auto_assigned_role and auto_assigned_role in member.roles:
            await member.remove_roles(auto_assigned_role)
            print(f"Removed auto-assigned role from {member.name}")

        display_name = member.display_name
        # Remove existing roles from the display name
        for role in ROLE_PRIORITY + ROLE_PRIORITY_LOWER:
            # Check for " | ROLE" pattern
            pattern_1 = f" | {role}"
            pattern_2 = f"|{role}"

            if pattern_1 in display_name:
                print(f"Removing '{pattern_1}' from {display_name}")
                display_name = display_name.replace(pattern_1, "").strip()
                print(f"New display name: {display_name}")
            elif pattern_2 in display_name:
                print(f"Removing '{pattern_2}' from {display_name}")
                display_name = display_name.replace(pattern_2, "").strip()
                print(f"New display name: {display_name}")
            
            # Check for standalone role
            if role in display_name.split(" "):
                print(f"Removing '{role}' from {display_name}")
                display_name = display_name.replace(role, "").strip()
                print(f"New display name: {display_name}")

        new_nickname = f"{display_name} | {highest_role}"
        if len(new_nickname) > 32:
            if highest_role == "Campus Ambassador":
                new_nickname = f"{display_name} | CA"
            else:
                excess_length = len(new_nickname) - 32
                truncated_display_name = display_name[:-excess_length]
                new_nickname = f"{truncated_display_name} | {highest_role}"

        if member != interaction.guild.owner:
            try:
                old_display_name = member.display_name  # Save the old display name before updating

                await member.edit(nick=new_nickname)  # Update nickname
                print(f"Updated nickname for {old_display_name} to {new_nickname}")

                # Log the username update after successful nickname change
                log_username_update(member, email, old_display_name, new_nickname)

                await interaction.followup.send(
                    f"{member.mention} Your username has been updated to `{new_nickname}` as per GSSoC guidelines. "
                    f"You are free to change it, but please ensure that **{highest_role}** remains part of your display name.",
                    ephemeral=True
                )
            except discord.Forbidden:
                print(f"Failed to change nickname for {member.name} due to missing permissions.")

        if member.id in welcome_messages:
            welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
            if welcome_channel:
                message_id = welcome_messages[member.id]["message_id"]
                try:
                    welcome_message = await welcome_channel.fetch_message(message_id)
                    await welcome_message.delete()
                    del welcome_messages[member.id]  # Remove the entry after successful deletion
                    save_welcome_log(welcome_messages)  # Update the log
                except discord.NotFound:
                    print(f"Welcome message {message_id} not found.")

        log_entry = {
            "discordusername": member.name,
            "discordid": member.id,
            "email": email,
            "roles": role_names,
            "time": datetime.now(timezone.utc).isoformat()  # Store with timezone-aware UTC timestamp
        }
        save_verification_log(log_entry)

    else:
        await interaction.response.send_message(f"Sorry, we couldn't verify your email at this time.", ephemeral=True)


#slash command to show bot developer details and bot details as embed
@tree.command(name="about", description="Shows information about the bot and the developer.", guild=discord.Object(id=GUILD_ID))
async def about(interaction: discord.Interaction):
    GSSOC_LOGO = "https://images-ext-1.discordapp.net/external/uhOfjzdx2Ybeh7T8RqVFgvs4ryRucs3_7sT51GNfgNQ/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1288156277351907389/94edf9346498881ddbc981cb9b82fe52.webp"
    # developer_avatar = "https://path_to_developer_avatar.png"  # Replace with the actual URL of the developer's avatar

    embed = discord.Embed(
        title="About GSSoC Manager",
        description="Welcome to the GirlScript Summer Of Code! 🤖\nThis bot helps streamlining the verification process and managing user roles, name for the GSSoC community while obeying the guidlines.",
        color=0xed8540,
        timestamp=datetime.now()
    )
    
    embed.set_author(name="GSSoC Manager", icon_url=GSSOC_LOGO)
    embed.set_thumbnail(url=GSSOC_LOGO)

    embed.add_field(name="Features", value="✨ Role assignment\n✨ Verification system\n✨ Welcome messages\n✨ Logging and more!", inline=False)
    embed.add_field(name="Developers", value="<a:priyanshu:1289235540100775967> [jindalpriyanshu101](https://github.com/jindalpriyanshu101)", inline=False)
    embed.add_field(name="Support", value="If you have any issues or questions, feel free to reach out to the developer or the support team.", inline=False)

    embed.set_footer(text="GSSoC Manager!", icon_url=GSSOC_LOGO)  # Set footer text and icon

    await interaction.response.send_message(embed=embed)

'''
@tree.command(name="whois", description="Find the user details by Discord username, ID, or email.", guild=discord.Object(id=GUILD_ID))
async def whois(interaction: discord.Interaction, query: str):
    user_data = None
    query_lower = query.lower()

    # Search in verification log
    verification_logs = load_verification_log()
    for log in verification_logs:
        # Compare with discord username, user ID or email
        if (log["discordusername"].lower() == query_lower or
            str(log["discordid"]) == query or
            log["email"].lower() == query_lower):
            user_data = log
            break

    # Search in username update log
    if not user_data:
        username_logs = load_username_log()
        for log in username_logs:
            if (log["discordusername"].lower() == query_lower or
                str(log["discordid"]) == query or
                log["email"].lower() == query_lower):
                user_data = log
                break

    # Search in failed attempts log
    if not user_data:
        for discord_id, email in failed_attempts.items():
            if (str(discord_id) == query or email.lower() == query_lower):
                user_data = {"discordid": discord_id, "email": email}
                break

    # Response logic
    if user_data:
        if "email" in user_data and "discordusername" in user_data:
            await interaction.response.send_message(
                f"**Discord User:** <@{user_data['discordid']}> \n**Email:** {user_data['email']}",
                # ephemeral=True
            )
        elif "discordid" in user_data:
            await interaction.response.send_message(
                f"**Discord User:** <@{user_data['discordid']}> \n**Email:** Not verified.",
                # ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"**Discord User:** Not found \n**Email:** {user_data['email']}",
                ephemeral=True
            )
    else:
        await interaction.response.send_message(
            "No matching user found. Please ensure the username, ID, or email is correct.",
            ephemeral=True
        )
'''


@tasks.loop(minutes=30)
async def cleanup_welcome_messages():
    now = datetime.now(timezone.utc)
    stale_messages = {member_id: data for member_id, data in welcome_messages.items()
                      if now - datetime.fromisoformat(data["timestamp"]) > timedelta(hours=1)}

    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        for member_id, data in stale_messages.items():
            try:
                message_id = data["message_id"]
                message = await welcome_channel.fetch_message(message_id)
                await message.delete()
                del welcome_messages[member_id]  # Remove the entry after successful deletion
            except discord.NotFound:
                print(f"Message {message_id} not found.")
        save_welcome_log(welcome_messages)  # Update the log

bot.run(TOKEN)
