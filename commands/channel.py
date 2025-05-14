import discord
import os
from discord.ext import commands

def setup(bot, tree, bot_data, admin_ids, homies):
    guild_id = int(os.getenv('DISCORD_GUILD_ID'))
    
    @tree.command(
        name="createchannel",
        description="Create a new text channel",
        guild=discord.Object(id=guild_id)
    )
    async def create_channel(
        interaction: discord.Interaction, 
        name: str, 
        category: discord.CategoryChannel = None,
        slowmode: int = 0, 
        nsfw: bool = False,
        topic: str = None
    ):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have permission to create channels.", ephemeral=True)
            return
        
        try:
            # Defer since channel creation might take some time
            await interaction.response.defer(ephemeral=False)
            
            # Set channel options
            channel_options = {
                "name": name,
                "slowmode_delay": slowmode,
                "nsfw": nsfw
            }
            
            if topic:
                channel_options["topic"] = topic
                
            if category:
                channel_options["category"] = category
            
            # Create the channel
            channel = await interaction.guild.create_text_channel(**channel_options)
            
            await interaction.followup.send(f"Channel {channel.mention} has been created.")
            
            # Log the action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Channel Created",
                        description=f"New channel {channel.mention} has been created",
                        color=discord.Color.green(),
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Created by", value=interaction.user.mention, inline=True)
                    if category:
                        embed.add_field(name="Category", value=category.name, inline=True)
                    
                    await log_channel.send(embed=embed)
                    
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to create channels.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
    
    @tree.command(
        name="createvoice",
        description="Create a new voice channel",
        guild=discord.Object(id=guild_id)
    )
    async def create_voice_channel(
        interaction: discord.Interaction, 
        name: str, 
        category: discord.CategoryChannel = None,
        user_limit: int = 0
    ):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have permission to create channels.", ephemeral=True)
            return
        
        try:
            # Defer since channel creation might take some time
            await interaction.response.defer(ephemeral=False)
            
            # Set channel options
            channel_options = {
                "name": name,
            }
            
            if user_limit > 0:
                channel_options["user_limit"] = user_limit
                
            if category:
                channel_options["category"] = category
            
            # Create the voice channel
            channel = await interaction.guild.create_voice_channel(**channel_options)
            
            await interaction.followup.send(f"Voice channel {channel.mention} has been created.")
            
            # Log the action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Voice Channel Created",
                        description=f"New voice channel {channel.mention} has been created",
                        color=discord.Color.green(),
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Created by", value=interaction.user.mention, inline=True)
                    if category:
                        embed.add_field(name="Category", value=category.name, inline=True)
                    if user_limit > 0:
                        embed.add_field(name="User Limit", value=str(user_limit), inline=True)
                    
                    await log_channel.send(embed=embed)
                    
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to create voice channels.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
    
    @tree.command(
        name="deletechannel",
        description="Delete a channel",
        guild=discord.Object(id=guild_id)
    )
    async def delete_channel(
        interaction: discord.Interaction, 
        channel: discord.abc.GuildChannel,
        reason: str = "No reason provided"
    ):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have permission to delete channels.", ephemeral=True)
            return
        
        try:
            # Store channel details before deletion for logging
            channel_name = channel.name
            channel_type = "Text" if isinstance(channel, discord.TextChannel) else "Voice"
            
            # Confirm deletion
            await interaction.response.send_message(
                f"Channel {channel.mention} will be deleted. Reason: {reason}",
                ephemeral=True
            )
            
            # Delete the channel
            await channel.delete(reason=f"Deleted by {interaction.user.name}: {reason}")
            
            # Send followup (as the original channel is now deleted)
            await interaction.followup.send(f"Channel '{channel_name}' has been deleted.", ephemeral=False)
            
            # Log the action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Channel Deleted",
                        description=f"{channel_type} channel '{channel_name}' has been deleted",
                        color=discord.Color.red(),
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Deleted by", value=interaction.user.mention, inline=True)
                    embed.add_field(name="Reason", value=reason, inline=True)
                    
                    await log_channel.send(embed=embed)
                    
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to delete this channel.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
    
    @tree.command(
        name="slowmode",
        description="Set slowmode for a text channel",
        guild=discord.Object(id=guild_id)
    )
    async def set_slowmode(
        interaction: discord.Interaction, 
        channel: discord.TextChannel,
        seconds: int = 0
    ):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have permission to modify channels.", ephemeral=True)
            return
        
        try:
            # Validate seconds
            if seconds < 0:
                await interaction.response.send_message("Slowmode delay must be a non-negative number.", ephemeral=True)
                return
                
            if seconds > 21600:  # Discord's max is 6 hours (21600 seconds)
                await interaction.response.send_message("Slowmode delay cannot exceed 6 hours (21600 seconds).", ephemeral=True)
                return
            
            # Set slowmode
            await channel.edit(slowmode_delay=seconds)
            
            if seconds == 0:
                await interaction.response.send_message(f"Slowmode has been disabled in {channel.mention}.")
            else:
                time_str = f"{seconds} second{'s' if seconds != 1 else ''}"
                await interaction.response.send_message(f"Slowmode in {channel.mention} has been set to {time_str}.")
            
            # Log the action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    if seconds == 0:
                        action = "disabled"
                    else:
                        time_str = f"{seconds} second{'s' if seconds != 1 else ''}"
                        action = f"set to {time_str}"
                        
                    embed = discord.Embed(
                        title="Slowmode Changed",
                        description=f"Slowmode in {channel.mention} has been {action}",
                        color=discord.Color.blue(),
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Modified by", value=interaction.user.mention, inline=True)
                    
                    await log_channel.send(embed=embed)
                    
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to modify this channel.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
            
    # Lockdown command - lock all channels or a specific set of channels
    @tree.command(
        name="lockdown",
        description="Lock multiple channels at once to prevent messaging",
        guild=discord.Object(id=guild_id)
    )
    async def lockdown(
        interaction: discord.Interaction,
        reason: str = "Server lockdown",
        category: discord.CategoryChannel = None  # Optional: lock only channels in this category
    ):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use the lockdown command.", ephemeral=True)
            return
            
        try:
            await interaction.response.defer(ephemeral=False)
            
            # Determine which channels to lock
            if category:
                channels = category.channels
                scope = f"channels in category '{category.name}'"
            else:
                channels = [c for c in interaction.guild.channels if isinstance(c, discord.TextChannel)]
                scope = "all text channels"
                
            # Count for success/failure tracking
            locked_count = 0
            failed_count = 0
            
            # Lock each channel
            for channel in channels:
                if isinstance(channel, discord.TextChannel):
                    try:
                        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
                        locked_count += 1
                    except:
                        failed_count += 1
            
            # Build result message
            result = f"Lockdown complete: {locked_count} channels locked"
            if failed_count > 0:
                result += f", {failed_count} channels failed"
                
            # Send results
            await interaction.followup.send(f"{result}\nReason: {reason}")
            
            # Log the action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Server Lockdown",
                        description=f"{interaction.user.mention} has locked {scope}",
                        color=discord.Color.red(),
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)
                    embed.add_field(name="Results", value=result, inline=False)
                    
                    await log_channel.send(embed=embed)
                    
        except Exception as e:
            await interaction.followup.send(f"An error occurred during lockdown: {str(e)}", ephemeral=True)
            
    # Unlock command - unlock all channels or a specific set of channels
    @tree.command(
        name="unlockdown",
        description="Unlock multiple channels at once to restore messaging",
        guild=discord.Object(id=guild_id)
    )
    async def unlockdown(
        interaction: discord.Interaction,
        category: discord.CategoryChannel = None  # Optional: unlock only channels in this category
    ):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use the unlockdown command.", ephemeral=True)
            return
            
        try:
            await interaction.response.defer(ephemeral=False)
            
            # Determine which channels to unlock
            if category:
                channels = category.channels
                scope = f"channels in category '{category.name}'"
            else:
                channels = [c for c in interaction.guild.channels if isinstance(c, discord.TextChannel)]
                scope = "all text channels"
                
            # Count for success/failure tracking
            unlocked_count = 0
            failed_count = 0
            
            # Unlock each channel
            for channel in channels:
                if isinstance(channel, discord.TextChannel):
                    try:
                        await channel.set_permissions(interaction.guild.default_role, send_messages=None)
                        unlocked_count += 1
                    except:
                        failed_count += 1
            
            # Build result message
            result = f"Lockdown lifted: {unlocked_count} channels unlocked"
            if failed_count > 0:
                result += f", {failed_count} channels failed"
                
            # Send results
            await interaction.followup.send(result)
            
            # Log the action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Server Unlockdown",
                        description=f"{interaction.user.mention} has unlocked {scope}",
                        color=discord.Color.green(),
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Results", value=result, inline=False)
                    
                    await log_channel.send(embed=embed)
                    
        except Exception as e:
            await interaction.followup.send(f"An error occurred during unlockdown: {str(e)}", ephemeral=True) 