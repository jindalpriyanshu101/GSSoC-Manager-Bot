import discord
import os
from datetime import timedelta

def setup(bot, tree, bot_data, admin_ids, homies):
    guild_id = int(os.getenv('DISCORD_GUILD_ID'))
    
    @tree.command(
        name="timeout", 
        description="Timeout a user for a specified duration", 
        guild=discord.Object(id=guild_id)
    )
    async def timeout(interaction: discord.Interaction, user: discord.Member, 
                     duration: int = 5, unit: str = "minutes", reason: str = "No reason provided"):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        # Convert duration to timedelta
        time_units = {
            "minutes": 60,
            "hours": 3600,
            "days": 86400
        }
        
        if unit not in time_units:
            await interaction.response.send_message(f"Invalid time unit. Use: {', '.join(time_units.keys())}", ephemeral=True)
            return
            
        timeout_duration = timedelta(seconds=duration * time_units[unit])
        
        # Apply timeout
        try:
            await user.timeout(timeout_duration, reason=reason)
            await interaction.response.send_message(
                f"{user.mention} has been timed out for {duration} {unit} | Reason: {reason}", 
                ephemeral=False
            )
            
            # Log the timeout action if log channel exists
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="User Timeout",
                        description=f"{user.mention} has been timed out",
                        color=discord.Color.orange(),
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Duration", value=f"{duration} {unit}", inline=True)
                    embed.add_field(name="Reason", value=reason, inline=True)
                    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
                    embed.set_footer(text=f"ID: {user.id}")
                    
                    await log_channel.send(embed=embed)
                    
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to timeout this user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True) 