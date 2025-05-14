import discord
import os
import json
from datetime import datetime

# File to store warning data
warnings_file = 'warnings.json'

def setup(bot, tree, bot_data, admin_ids, homies):
    guild_id = int(os.getenv('DISCORD_GUILD_ID'))
    
    # Load warnings data
    warnings_data = load_warnings()
    
    @tree.command(
        name="warn",
        description="Warn a user for rule violations",
        guild=discord.Object(id=guild_id)
    )
    async def warn(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        # Add warning to the user
        guild_id_str = str(interaction.guild.id)
        user_id_str = str(user.id)
        
        # Initialize guild entry if it doesn't exist
        if guild_id_str not in warnings_data:
            warnings_data[guild_id_str] = {}
            
        # Initialize user entry if it doesn't exist
        if user_id_str not in warnings_data[guild_id_str]:
            warnings_data[guild_id_str][user_id_str] = {
                "count": 0,
                "warnings": []
            }
        
        # Add the warning
        warning_entry = {
            "reason": reason,
            "moderator": str(interaction.user.id),
            "timestamp": datetime.now().isoformat()
        }
        
        warnings_data[guild_id_str][user_id_str]["warnings"].append(warning_entry)
        warnings_data[guild_id_str][user_id_str]["count"] += 1
        
        # Save the updated warnings data
        save_warnings(warnings_data)
        
        # Get the total number of warnings for this user
        warning_count = warnings_data[guild_id_str][user_id_str]["count"]
        
        # Send confirmation
        await interaction.response.send_message(
            f"{user.mention} has been warned | Reason: {reason}\nTotal warnings: {warning_count}",
            ephemeral=False
        )
        
        # DM the user about their warning
        try:
            embed = discord.Embed(
                title=f"Warning in {interaction.guild.name}",
                description=f"You have been warned by a moderator.",
                color=discord.Color.yellow(),
                timestamp=interaction.created_at
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Warning Count", value=str(warning_count), inline=False)
            
            # Add automatic consequences based on warning count
            if warning_count >= 3:
                embed.add_field(
                    name="Note", 
                    value="You have accumulated 3 or more warnings. Further violations may result in a mute or ban.",
                    inline=False
                )
                
            await user.send(embed=embed)
        except discord.Forbidden:
            # User has DMs disabled
            await interaction.followup.send("Could not DM user about their warning.", ephemeral=True)
        
        # Log the warning
        log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
        if log_channel_id:
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed(
                    title="User Warned",
                    description=f"{user.mention} has been warned",
                    color=discord.Color.yellow(),
                    timestamp=interaction.created_at
                )
                embed.add_field(name="Reason", value=reason, inline=True)
                embed.add_field(name="Warning Count", value=str(warning_count), inline=True)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
                embed.set_footer(text=f"ID: {user.id}")
                
                await log_channel.send(embed=embed)
        
        # Take automated actions based on warning count
        if warning_count == 3:
            # Timeout for 1 hour at 3 warnings
            try:
                await user.timeout(discord.utils.utcnow() + discord.utils.timedelta(hours=1), 
                                 reason="Automatic timeout after 3 warnings")
                await interaction.followup.send(
                    f"{user.mention} has been automatically timed out for 1 hour after receiving 3 warnings.",
                    ephemeral=False
                )
            except discord.Forbidden:
                await interaction.followup.send(
                    "Could not apply automatic timeout. Please check bot permissions.",
                    ephemeral=True
                )
    
    @tree.command(
        name="warnings",
        description="Check warnings for a user",
        guild=discord.Object(id=guild_id)
    )
    async def check_warnings(interaction: discord.Interaction, user: discord.Member):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.moderate_members:
            if interaction.user.id != user.id:  # Users can check their own warnings
                await interaction.response.send_message("You do not have permission to check other users' warnings.", ephemeral=True)
                return
        
        guild_id_str = str(interaction.guild.id)
        user_id_str = str(user.id)
        
        # Check if user has any warnings
        if (guild_id_str not in warnings_data or 
            user_id_str not in warnings_data[guild_id_str] or 
            warnings_data[guild_id_str][user_id_str]["count"] == 0):
            await interaction.response.send_message(f"{user.mention} has no warnings.", ephemeral=True)
            return
        
        # Display warnings
        warning_count = warnings_data[guild_id_str][user_id_str]["count"]
        warnings = warnings_data[guild_id_str][user_id_str]["warnings"]
        
        embed = discord.Embed(
            title=f"Warnings for {user.name}",
            description=f"Total warnings: {warning_count}",
            color=discord.Color.yellow(),
            timestamp=interaction.created_at
        )
        
        # Show the 5 most recent warnings
        for i, warning in enumerate(warnings[-5:], 1):
            moderator = interaction.guild.get_member(int(warning["moderator"]))
            moderator_name = moderator.mention if moderator else "Unknown Moderator"
            
            embed.add_field(
                name=f"Warning {i}",
                value=f"**Reason:** {warning['reason']}\n" +
                      f"**Moderator:** {moderator_name}\n" +
                      f"**Date:** <t:{int(datetime.fromisoformat(warning['timestamp']).timestamp())}:R>",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @tree.command(
        name="clearwarnings",
        description="Clear all warnings for a user",
        guild=discord.Object(id=guild_id)
    )
    async def clear_warnings(interaction: discord.Interaction, user: discord.Member, 
                            clear_all: bool = True, warning_index: int = None):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to clear warnings.", ephemeral=True)
            return
        
        guild_id_str = str(interaction.guild.id)
        user_id_str = str(user.id)
        
        # Check if user has any warnings
        if (guild_id_str not in warnings_data or 
            user_id_str not in warnings_data[guild_id_str] or 
            warnings_data[guild_id_str][user_id_str]["count"] == 0):
            await interaction.response.send_message(f"{user.mention} has no warnings to clear.", ephemeral=True)
            return
        
        if clear_all:
            # Clear all warnings
            warnings_data[guild_id_str][user_id_str] = {
                "count": 0,
                "warnings": []
            }
            save_warnings(warnings_data)
            
            await interaction.response.send_message(
                f"All warnings for {user.mention} have been cleared.",
                ephemeral=False
            )
        elif warning_index is not None:
            # Clear a specific warning
            if warning_index < 1 or warning_index > len(warnings_data[guild_id_str][user_id_str]["warnings"]):
                await interaction.response.send_message(
                    f"Invalid warning index. User has {len(warnings_data[guild_id_str][user_id_str]['warnings'])} warnings.",
                    ephemeral=True
                )
                return
            
            # Remove the warning
            warnings_data[guild_id_str][user_id_str]["warnings"].pop(warning_index - 1)
            warnings_data[guild_id_str][user_id_str]["count"] -= 1
            save_warnings(warnings_data)
            
            await interaction.response.send_message(
                f"Warning #{warning_index} for {user.mention} has been cleared.",
                ephemeral=False
            )
        
        # Log the warning clear
        log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
        if log_channel_id:
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:
                if clear_all:
                    message = f"All warnings for {user.mention} have been cleared"
                else:
                    message = f"Warning #{warning_index} for {user.mention} has been cleared"
                    
                embed = discord.Embed(
                    title="Warnings Cleared",
                    description=message,
                    color=discord.Color.green(),
                    timestamp=interaction.created_at
                )
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
                embed.set_footer(text=f"ID: {user.id}")
                
                await log_channel.send(embed=embed)


def load_warnings():
    if os.path.exists(warnings_file) and os.stat(warnings_file).st_size > 0:
        try:
            with open(warnings_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_warnings(warnings_data):
    with open(warnings_file, 'w') as f:
        json.dump(warnings_data, f, indent=4) 